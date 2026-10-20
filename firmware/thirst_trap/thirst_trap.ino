/*
  THIRST TRAP — timed plant waterer, ATtiny85, 3xAA, sleeps between drinks.

  Board:   ATTinyCore -> ATtiny25/45/85 (No bootloader)
  Clock:   1 MHz internal     BOD: disabled     millis(): enabled
  Program: Arduino-as-ISP or USBasp. Do "Burn Bootloader" once to set fuses, then upload.

  Pins (DIP-8 physical pin in brackets):
    PB0 [5]  -> MOSFET gate via 220R, 100k gate-to-GND
    PB1 [6]  -> LED (via 1k) AND top of both pots (pots only powered while being read)
    PB2 [7]  -> button to GND (internal pull-up, wakes the chip)
    PB3 [2]  -> INTERVAL pot wiper  (ADC3)
    PB4 [3]  -> DURATION pot wiper  (ADC2)
    Pot bottoms -> GND.  VCC [8] -> battery +, GND [4] -> battery -

  Use:
    Twist dials. Changes apply at the next watering or next button press.
    Short press  = blink out the interval setting, water now, restart the countdown
                   (so press it at the time of day you want it to water).
    Hold > 0.8s  = pump runs while held (priming / topping up / measuring flow).
    LED blips once a minute = alive.  Double blip = batteries low.
    Triple-fast blip and no watering = batteries flat.
*/

#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>
#include <avr/power.h>

#define PIN_PUMP  0   // PB0
#define PIN_LED   1   // PB1
#define PIN_BTN   2   // PB2

// Watchdog "8 s" is really 7-9 s depending on chip and temperature.
// Calibrate: time 10 heartbeats (one per 8 ticks) with a stopwatch, divide by 80, put the result here.
#define TICK_MS   8000UL

const uint16_t INTERVAL_H[8]  = { 6, 12, 24, 36, 48, 72, 96, 168 };
const uint8_t  DURATION_S[8]  = { 3, 5, 8, 12, 20, 30, 45, 60 };

#define VBAT_LOW_MV   3400   // warn
#define VBAT_FLAT_MV  3000   // stop pumping (3 x 1.0 V)
#define MANUAL_MAX_MS 120000UL

volatile bool btnFlag = false;
ISR(WDT_vect)    { }                 // just wakes us
ISR(PCINT0_vect) { btnFlag = true; }

uint32_t ticks = 0;
uint32_t ticksNeeded = 0;
uint8_t  intIdx = 2, durIdx = 3;

// ---------- ADC (raw, Vcc as reference) ----------
uint16_t adcRead(uint8_t mux, uint8_t settleMs) {
  power_adc_enable();
  ADMUX  = mux & 0x0F;                                  // REFS = 00 -> Vcc reference
  ADCSRA = _BV(ADEN) | _BV(ADPS1) | _BV(ADPS0);         // /8 -> 125 kHz at 1 MHz
  delay(settleMs);
  ADCSRA |= _BV(ADSC); while (ADCSRA & _BV(ADSC));      // throw away first
  ADCSRA |= _BV(ADSC); while (ADCSRA & _BV(ADSC));
  uint16_t v = ADC;
  ADCSRA = 0;
  power_adc_disable();
  return v;
}

uint16_t vccMilliVolts() {
  uint16_t a = adcRead(0x0C, 5);                        // MUX 1100 = 1.1 V bandgap
  if (a == 0) return 0;
  return (uint16_t)((1100UL * 1023UL) / a);             // bandgap is +/-10%: fine for this
}

uint8_t toIndex(uint16_t a) {
  uint8_t i = (uint8_t)(((uint32_t)a * 8UL) / 1000UL);  // 1000 not 1024: allows for sag on PB1
  return i > 7 ? 7 : i;
}

void readSettings() {
  digitalWrite(PIN_LED, HIGH);                          // powers the pots (LED flashes, that's fine)
  delay(2);
  intIdx = toIndex(adcRead(3, 1));                      // PB3 = ADC3
  durIdx = toIndex(adcRead(2, 1));                      // PB4 = ADC2
  digitalWrite(PIN_LED, LOW);
  ticksNeeded = (uint32_t)INTERVAL_H[intIdx] * 3600000UL / TICK_MS;
}

// ---------- LED ----------
void blip(uint8_t n, uint16_t onMs, uint16_t offMs) {
  for (uint8_t i = 0; i < n; i++) {
    digitalWrite(PIN_LED, HIGH); delay(onMs);
    digitalWrite(PIN_LED, LOW);  delay(offMs);
  }
}

// ---------- pump ----------
void pumpFor(uint16_t seconds) {
  if (vccMilliVolts() < VBAT_FLAT_MV) { blip(3, 40, 120); return; }
  digitalWrite(PIN_PUMP, HIGH);
  for (uint16_t s = 0; s < seconds; s++) delay(1000);
  digitalWrite(PIN_PUMP, LOW);
}

void water() {
  readSettings();
  pumpFor(DURATION_S[durIdx]);
  ticks = 0;
}

// ---------- sleep ----------
void sleep8s() {
  MCUSR &= ~_BV(WDRF);
  WDTCR = _BV(WDCE) | _BV(WDE);
  WDTCR = _BV(WDIE) | _BV(WDP3) | _BV(WDP0);            // interrupt only, ~8 s
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  cli();
  sleep_enable();
#if defined(BODS)
  sleep_bod_disable();
#endif
  sei();
  sleep_cpu();
  sleep_disable();
}

// ---------- button ----------
void handleButton() {
  delay(30);
  if (digitalRead(PIN_BTN) == HIGH) { btnFlag = false; return; }   // bounce / release edge
  uint32_t t0 = millis();
  while (digitalRead(PIN_BTN) == LOW && millis() - t0 < 800) { }
  if (digitalRead(PIN_BTN) == LOW) {
    // held: manual pump
    if (vccMilliVolts() >= VBAT_FLAT_MV) {
      digitalWrite(PIN_PUMP, HIGH);
      uint32_t t1 = millis();
      while (digitalRead(PIN_BTN) == LOW && millis() - t1 < MANUAL_MAX_MS) { }
      digitalWrite(PIN_PUMP, LOW);
    } else {
      blip(3, 40, 120);
    }
  } else {
    // short press: show interval (1..8 slow blinks), then water and restart countdown
    readSettings();
    delay(400);
    blip(intIdx + 1, 250, 250);
    delay(400);
    water();
  }
  while (digitalRead(PIN_BTN) == LOW) { }
  delay(30);
  btnFlag = false;
}

void setup() {
  pinMode(PIN_PUMP, OUTPUT); digitalWrite(PIN_PUMP, LOW);
  pinMode(PIN_LED,  OUTPUT); digitalWrite(PIN_LED,  LOW);
  pinMode(PIN_BTN,  INPUT_PULLUP);

  DIDR0 = _BV(ADC3D) | _BV(ADC2D);                       // no digital buffers on pot pins
  ACSR |= _BV(ACD);                                       // analogue comparator off
  power_timer1_disable();
  power_usi_disable();
  power_adc_disable();

  GIMSK |= _BV(PCIE);
  PCMSK |= _BV(PCINT2);

  readSettings();
  blip(intIdx + 1, 250, 250);                             // hello: shows interval setting
  ticks = 0;
}

void loop() {
  sleep8s();

  if (btnFlag) { handleButton(); return; }

  ticks++;
  if (ticks >= ticksNeeded) { water(); return; }

  if ((ticks & 7) == 0) {                                  // ~once a minute
    uint16_t mv = vccMilliVolts();
    if (mv < VBAT_LOW_MV) blip(2, 3, 150);
    else                  blip(1, 3, 0);
  }
}
