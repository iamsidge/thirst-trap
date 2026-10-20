// THIRST TRAP — clip-on, battery-powered, timed plant waterer
// Parametric enclosure. Units: mm.  Print in PETG (water + sunlight). 0.2mm layers, 3 walls.
//
// Render one part at a time:  openscad -D 'part="box"' -o box.stl thirst_trap.scad
// parts: box | lid | clip | stake | sinker | knob | preview | inside | exploded
// (inside/exploded include mock pump, batteries, board, tubes and wiring for checking fit)
//
// MEASURE YOUR PUMP AND BATTERY HOLDER and adjust the numbers below before printing.
// Cheap AliExpress parts vary by a few mm between sellers.

part = "preview";

$fn = 56;

// ---------- enclosure ----------
wall   = 2.0;
lid_t  = 2.4;
in_w   = 74;    // inner width  (X)
in_h   = 112;   // inner height (Y, vertical when hung on pot)
in_d   = 34;    // inner depth  (Z, back wall -> lid)
r_out  = 4;     // outer corner radius

ow = in_w + 2*wall;
oh = in_h + 2*wall;
od = in_d + wall;           // box is open at the front (z = od), lid closes it

// ---------- bought parts ----------
tube_od   = 6.0;   // silicone tube 4mm ID / 6mm OD
tube_clr  = 0.5;
pump_d    = 27.5;  // diaphragm pump motor/head diameter
pump_body = 48;    // pump body length between cradles' outer faces (nozzles excluded)
bat_w     = 47;    // 3xAA side-by-side holder
bat_l     = 58;
pot_hole  = 7.4;   // WH148 16mm pot, M7 bushing
btn_hole  = 7.2;   // PBS-110 style 7mm momentary button
led_hole  = 5.2;   // 5mm LED (push-fit, dab of glue)

// ---------- screws ----------
lid_screw_pilot = 2.6;   // M3 self-tapping into boss (or M3 thread-forming)
lid_screw_clear = 3.4;
m3_clear  = 3.4;
m3_nut_af = 5.7;         // across flats + clearance
m3_nut_t  = 2.6;

// ---------- pot clip ----------
clip_w     = 24;   // keep narrow so it sits on a curved rim
clip_t     = 3.2;
rim_t      = 7;    // pot rim/wall thickness + ~1mm. MEASURE YOUR POT.
clip_drop  = 22;   // how far the inner leg reaches down inside the pot
clip_rise  = 8;    // how far the hook sits above the box top
clip_below = 14;   // plate length below box top (screws sit in here)

// ---------- labels ----------
title     = "THIRST TRAP";
int_lbls  = ["6h","12h","1d","36h","2d","3d","4d","7d"];
dur_lbls  = ["3s","5s","8s","12","20","30","45","60s"];
pot_sweep = 300;   // WH148 rotation in degrees
engrave   = 0.6;
font      = "DejaVu Sans:style=Bold";

// ---------- derived layout (absolute box coords; x right, y up, z out of front) ----------
pc_y  = wall + pump_d/2 + 1;     // pump axis
pc_z  = wall + pump_d/2 + 1;
bat_y0 = pc_y + pump_d/2 + 4;    // battery holder bottom edge
boss_x = [wall + 2.5, ow - wall - 2.5];
boss_y = [50, 100];
boss_r = 4.5;
clip_sx = [ow/2 - 8, ow/2 + 8];  // clip screws
clip_sy = oh - 5;
dial1 = [ow/2, 98];              // interval
dial2 = [ow/2, 66];              // duration
btn   = [ow/2 + 12, 40];
led   = [ow/2 - 12, 40];

module rbox(w, h, d, r) {
    hull() for (x = [r, w - r], y = [r, h - r]) translate([x, y, 0]) cylinder(r = r, h = d);
}

// ================= BOX =================
module box() {
    difference() {
        union() {
            difference() {
                rbox(ow, oh, od, r_out);
                translate([wall, wall, wall]) rbox(in_w, in_h, od, max(r_out - wall, 0.6));
            }
            // lid screw bosses (clipped to outer shape)
            intersection() {
                rbox(ow, oh, od, r_out);
                for (x = boss_x, y = boss_y) translate([x, y, 0]) cylinder(r = boss_r, h = od);
            }
            // pump saddles
            for (sx = [ow/2 - pump_body/2 + 3, ow/2 + pump_body/2 - 3])
                difference() {
                    translate([sx - 3, wall, wall]) cube([6, pump_d + 2, pump_d/2 + 1]);
                    translate([sx - 4, pc_y, pc_z]) rotate([0, 90, 0]) cylinder(d = pump_d + 0.6, h = 8);
                }
            // battery holder locating ribs
            for (x = [ow/2 - bat_w/2 - 2, ow/2 + bat_w/2 + 0.5])
                translate([x, bat_y0, wall]) cube([1.5, bat_l, 2.5]);
            // nut bosses for the pot clip (also hold the perfboard on foam tape)
            for (x = clip_sx) translate([x, clip_sy - 1, wall]) cylinder(r = 4.5, h = 5);
        }
        // lid screw pilots
        for (x = boss_x, y = boss_y) translate([x, y, od - 14]) cylinder(d = lid_screw_pilot, h = 15);
        // clip screws + nut traps
        for (x = clip_sx) {
            translate([x, clip_sy - 1, -1]) cylinder(d = m3_clear, h = 10);
            translate([x, clip_sy - 1, wall + 5 - m3_nut_t]) cylinder(d = m3_nut_af / cos(30), h = 5, $fn = 6);
        }
        // zip-tie slots either side of each saddle
        for (sx = [ow/2 - pump_body/2 + 3, ow/2 + pump_body/2 - 3], dy = [-1, 1])
            translate([sx - 2, pc_y + dy * (pump_d/2 + 2.5) - 1.5, -1]) cube([4, 3, wall + 2]);
        // inlet: bottom, left end
        translate([wall + 7, -1, in_d/2 + wall]) rotate([-90, 0, 0]) cylinder(d = tube_od + tube_clr, h = wall + 2);
        // outlet: top, right end, in the front void ahead of the battery
        translate([ow - wall - 12, oh - wall - 1, od - 9]) rotate([-90, 0, 0]) cylinder(d = tube_od + tube_clr, h = wall + 2);
        // drain holes
        for (x = [ow/2 - 12, ow/2 + 12]) translate([x, -1, wall + 6]) rotate([-90, 0, 0]) cylinder(d = 3, h = wall + 2);
    }
}

// ================= LID (modelled in place: outer face at z=lid_t, lip pointing -z) =================
module dial_marks(c, lbls, name) {
    n = len(lbls);
    for (i = [0 : n - 1]) {
        a = -pot_sweep/2 + pot_sweep * (i + 0.5) / n;   // clockwise from 12 o'clock
        ang = 90 - a;
        translate([c[0], c[1], 0]) {
            rotate(ang) translate([9.5, -0.4]) square([2.2, 0.8]);
            translate([15.2 * cos(ang), 15.2 * sin(ang)])
                text(lbls[i], size = 2.4, font = font, halign = "center", valign = "center");
        }
    }
    translate([c[0], c[1] - 12.5]) text(name, size = 2.2, font = font, halign = "center", valign = "center");
}

module lid_inplace() {
    lip_w = in_w - 0.6; lip_h = in_h - 0.6;
    difference() {
        union() {
            rbox(ow, oh, lid_t, r_out);
            // locating lip
            translate([wall + 0.3, wall + 0.3, -3])
                difference() {
                    rbox(lip_w, lip_h, 3, max(r_out - wall, 0.6));
                    translate([1.6, 1.6, -1]) rbox(lip_w - 3.2, lip_h - 3.2, 5, 0.6);
                }
        }
        // clear the bosses
        for (x = boss_x, y = boss_y) translate([x, y, -4]) cylinder(r = boss_r + 0.6, h = 4);
        // screw holes + countersink
        for (x = boss_x, y = boss_y) {
            translate([x, y, -5]) cylinder(d = lid_screw_clear, h = 10);
            translate([x, y, lid_t - 1.7]) cylinder(d1 = lid_screw_clear, d2 = 6.4, h = 1.71);
        }
        // controls
        for (p = [dial1, dial2]) translate([p[0], p[1], -5]) cylinder(d = pot_hole, h = 10);
        translate([btn[0], btn[1], -5]) cylinder(d = btn_hole, h = 10);
        translate([led[0], led[1], -5]) cylinder(d = led_hole, h = 10);
        // engraving on the outer face
        translate([0, 0, lid_t - engrave]) linear_extrude(engrave + 0.1) {
            dial_marks(dial1, int_lbls, "EVERY");
            dial_marks(dial2, dur_lbls, "FOR");
            translate([btn[0], btn[1] - 7]) text("WATER", size = 2.2, font = font, halign = "center", valign = "center");
            translate([led[0], led[1] - 7]) text("ALIVE", size = 2.2, font = font, halign = "center", valign = "center");
            translate([ow/2, 16]) text(title, size = 5, font = font, halign = "center", valign = "center");
        }
    }
}
module lid() { translate([0, oh, lid_t]) rotate([180, 0, 0]) lid_inplace(); }   // print-ready, face down

// ================= POT CLIP (print lying on its side: profile flat on bed) =================
// profile coords: u = toward/into pot (u=0 touches box back), v = up (v=0 at plate bottom)
module clip_profile() {
    H = clip_below + clip_rise;
    gi = clip_t + rim_t;              // inner face of the inner leg
    union() {
        square([clip_t, H]);                                  // plate
        translate([0, H - clip_t]) square([gi + clip_t, clip_t]);  // bridge over rim
        translate([gi, H - clip_drop]) square([clip_t, clip_drop]); // inner leg
        translate([gi, H - clip_drop]) intersection() {      // grip bump
            translate([0, 2]) circle(r = 1.2);
            translate([-2, 0]) square([2, 4]);
        }
        // fillets
        translate([clip_t, H - clip_t - 2]) difference() { square(2); translate([2, 0]) circle(r = 2); }
        translate([gi - 2, H - clip_t - 2]) difference() { square(2); circle(r = 2); }
    }
}
module clip() {
    difference() {
        linear_extrude(clip_w) clip_profile();
        for (dx = [-8, 8])
            translate([-1, clip_below - 6, clip_w/2 + dx]) rotate([0, 90, 0]) {
                cylinder(d = m3_clear, h = clip_t + 2);
            }
        // counterbore for M3 heads on the pot side
        for (dx = [-8, 8])
            translate([clip_t - 1.6, clip_below - 6, clip_w/2 + dx]) rotate([0, 90, 0]) cylinder(d = 6.2, h = 2);
    }
}

// ================= DRIP STAKE =================
module stake() {
    L = 70;
    difference() {
        union() {
            cylinder(d = 11, h = 14);                                   // tube socket
            translate([0, 0, -L + 14]) cylinder(d1 = 2.5, d2 = 8, h = L - 14);  // spike (printed point-down? no: print upside down, see README)
            translate([0, 0, 12]) cylinder(d1 = 11, d2 = 14, h = 2);    // push collar
        }
        translate([0, 0, 4]) cylinder(d = tube_od - 0.3, h = 20);       // tight push-fit on tube OD
        translate([0, 0, -40]) cylinder(d = 2.2, h = 46);               // water channel
        for (a = [0, 120, 240]) translate([0, 0, -32]) rotate([0, 90, a]) cylinder(d = 1.8, h = 10); // side outlets
    }
}

// ================= BOTTLE SINKER / STRAINER =================
// Keeps the intake on the bottom of the bottle. Push an M8 nut into the base for weight.
module sinker() {
    difference() {
        cylinder(d = 18, h = 22);
        translate([0, 0, 12]) cylinder(d = tube_od - 0.3, h = 11);       // tube push-fit
        translate([0, 0, -1]) cylinder(d = 3, h = 14);                   // channel
        translate([0, 0, -0.01]) cylinder(d = 13.4 / cos(30), h = 6.8, $fn = 6); // M8 nut pocket
        for (a = [0, 90]) translate([0, 0, 9]) rotate([90, 0, a]) translate([0, 0, -10]) cylinder(d = 2.5, h = 20); // side inlets
    }
}

// ================= KNOB (WH148 6mm knurled/D shaft) =================
module knob() {
    difference() {
        union() {
            cylinder(d = 16, h = 12);
            translate([-0.8, 4, 12]) cube([1.6, 4.5, 1.2]);              // pointer ridge
            for (a = [0 : 20 : 359]) rotate(a) translate([8, 0, 0]) cylinder(d = 1.6, h = 12, $fn = 12); // grip
        }
        translate([0, 0, -1]) difference() {                             // D shaft
            cylinder(d = 6.2, h = 11);
            translate([1.55, -4, -1]) cube([4, 8, 14]);
        }
    }
}

// ================= dispatch =================
if (part == "box")    box();
if (part == "lid")    lid();
if (part == "clip")   clip();
if (part == "stake")  rotate([180, 0, 0]) translate([0, 0, -16]) stake();   // print socket-down
if (part == "sinker") sinker();
if (part == "knob")   knob();
if (part == "preview") {
    color("seagreen") box();
    color("ghostwhite", 0.85) translate([0, 0, od]) lid_inplace();
    // clip, placed on the back
    color("orange") translate([ow/2 - clip_w/2, oh - clip_below, 0])
        multmatrix([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1]]) clip();
    for (p = [dial1, dial2]) color("dimgray") translate([p[0], p[1], od + lid_t]) knob();
}

// ================= MOCK COMPONENTS (visualisation only, not for printing) =================
module tube_path(pts, d = tube_od) {
    for (i = [0 : len(pts) - 2]) hull() { translate(pts[i]) sphere(d = d, $fn = 16); translate(pts[i + 1]) sphere(d = d, $fn = 16); }
}
module wire(pts, c) { color(c) tube_path(pts, 1.2); }

pump_x0 = ow/2 - pump_body/2;          // head end (left)
noz_in  = [pump_x0 - 7, pc_y - 5, pc_z];
noz_out = [pump_x0 - 7, pc_y + 5, pc_z];
board   = [ow/2 - 20, oh - wall - 21, wall + 5];   // perfboard origin (x, y, z of underside)
bx0 = ow/2 - bat_w/2;

module mock_box_parts() {
    // --- battery holder + 3xAA ---
    color("#222") difference() {
        translate([bx0, bat_y0, wall]) cube([bat_w, bat_l, 16]);
        translate([bx0 + 1, bat_y0 + 1, wall + 1.5]) cube([bat_w - 2, bat_l - 2, 20]);
    }
    for (i = [-1, 0, 1]) translate([ow/2 + i * 15, bat_y0 + 3.5, wall + 1.5 + 7.25]) rotate([-90, 0, 0]) {
        color("#c9a227") cylinder(d = 14.5, h = 44);
        color("#333") translate([0, 0, 44]) cylinder(d = 14.5, h = 6.5);
        color("silver") translate([0, 0, 50.5]) cylinder(d = 5, h = 0.8);
    }
    // --- pump: motor + head + nozzles ---
    translate([0, pc_y, pc_z]) rotate([0, 90, 0]) {
        color("silver")    translate([0, 0, pump_x0 + 18]) cylinder(d = 24, h = pump_body - 18);
        color("#1f4fa8")   translate([0, 0, pump_x0])      cylinder(d = pump_d, h = 18);
        color("#c0392b")   translate([-3, -8, pump_x0 + pump_body]) cube([6, 3, 3]);  // + tab
    }
    color("#1f4fa8") for (n = [noz_in, noz_out]) translate(n) rotate([0, 90, 0]) cylinder(d = 4, h = 8);
    // zip ties
    color("white") for (sx = [pump_x0 + 3, pump_x0 + pump_body - 3])
        translate([sx, pc_y, pc_z]) rotate([0, 90, 0]) difference() { cylinder(d = pump_d + 2.4, h = 3.6, center = true); cylinder(d = pump_d + 0.2, h = 4, center = true); }

    // --- perfboard with parts ---
    translate(board) {
        color("#b5853f") cube([40, 20, 1.6]);
        // ATtiny85 in socket
        color("#111") translate([4, 6, 1.6]) cube([10.2, 7.6, 3]);
        color("#222") translate([4.5, 6.6, 4.6]) cube([9.2, 6.4, 3.4]);
        color("white") translate([5.2, 9.8, 8.01]) cylinder(d = 1, h = 0.1);
        // MOSFET TO-220, laid flat
        color("#111") translate([18, 4, 1.6]) cube([10, 9, 4.5]);
        color("silver") translate([18, 13, 2.2]) cube([10, 6, 1.3]);
        color("silver") for (l = [0, 2.54, 5.08]) translate([20.4 + l, 0, 3]) cube([0.8, 4, 0.5]);
        // 220uF lying down
        color("#16365e") translate([31, 3, 1.6 + 3.2]) rotate([-90, 0, 0]) cylinder(d = 6.3, h = 11);
        // resistors + diode
        color("#d8c79a") for (p = [[18, 15.5], [24, 15.5]]) translate([p[0], p[1], 2.6]) rotate([0, 90, 0]) cylinder(d = 2, h = 5);
        color("#222") translate([31, 16, 2.8]) rotate([0, 90, 0]) cylinder(d = 2.6, h = 6);
        color("silver") translate([36.5, 16, 2.8]) rotate([0, 90, 0]) cylinder(d = 2.7, h = 0.8);
        // foam tape
        color("#eee", 0.6) for (x = [ow/2 - 8, ow/2 + 8] - [board[0], board[0]]) translate([x - 4, 18 - 13.5, -0.8]) cube([8, 9, 0.8]);
    }

    // --- tubes ---
    color("#9fd3e8", 0.9) {
        tube_path([noz_in, [wall + 7, pc_y - 6, wall + in_d/2], [wall + 7, wall + 1, wall + in_d/2], [wall + 7, -25, wall + in_d/2]]);
        tube_path([noz_out, [pump_x0 - 9, 33, 27], [ow - wall - 12, 33, 27], [ow - wall - 12, oh - 4, 27], [ow - wall - 12, oh + 20, 27]]);
    }

    // --- wiring ---
    bw = [board[0], board[1], board[2] + 1.6];
    wire([[bx0 + 3, bat_y0 + bat_l - 2, wall + 14], [bx0 + 3, bw[1] + 2, 12], [bw[0] + 6, bw[1] + 4, bw[2]]], "#d62728");  // batt +
    wire([[bx0 + bat_w - 3, bat_y0 + bat_l - 2, wall + 14], [bx0 + bat_w - 3, bw[1] + 2, 12], [bw[0] + 30, bw[1] + 2, bw[2]]], "#111");  // batt -
    wire([[pump_x0 + pump_body + 1, pc_y, pc_z + 2], [ow - wall - 5, 30, 24], [ow - wall - 5, bw[1] + 3, 14], [bw[0] + 36, bw[1] + 5, bw[2]]], "#d62728"); // pump +
    wire([[pump_x0 + pump_body + 1, pc_y - 3, pc_z - 2], [ow - wall - 7, 30, 22], [ow - wall - 7, bw[1] + 4, 13], [bw[0] + 22, bw[1] + 2, bw[2]]], "#111"); // pump -
    // ribbon up to the lid controls
    for (i = [0 : 4]) wire([[bw[0] + 8 + i * 1.3, bw[1] + 18, bw[2]], [bw[0] + 8 + i * 1.3, bw[1] + 18, 30], [ow/2 - 3 + i * 1.3, dial1[1] + 9, od - 4]],
        ["#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd", "#e377c2"][i]);
}

// controls hanging off the inside of the lid (lid in its closed position)
module mock_lid_parts() {
    for (p = [dial1, dial2]) translate([p[0], p[1], od]) {
        color("#2b5d2b") translate([0, 0, -9]) cylinder(d = 16, h = 9);
        color("silver") cylinder(d = 7, h = lid_t + 5);
        color("silver") translate([0, 0, lid_t]) cylinder(d = 10, h = 2, $fn = 6);
        color("silver") for (dx = [-5, 0, 5]) translate([dx - 1, -12, -6]) cube([2, 5, 0.4]);
    }
    translate([btn[0], btn[1], od]) {
        color("#111") translate([0, 0, -12]) cylinder(d = 8, h = 12);
        color("#c0392b") cylinder(d = 5, h = lid_t + 3);
    }
    translate([led[0], led[1], od - 4]) color("#ff3030", 0.8) { cylinder(d = 5, h = 4 + lid_t - 1.5); translate([0, 0, 4 + lid_t - 1.5]) sphere(d = 5); }
}

if (part == "inside") {               // lid off, laid face-down to the right so its controls show
    color("seagreen") box();
    mock_box_parts();
    translate([2 * ow + 15, 0, lid_t]) rotate([0, 180, 0]) translate([0, 0, -od]) {
        color("ghostwhite") translate([0, 0, od]) lid_inplace();
        mock_lid_parts();
    }
}
if (part == "exploded") {
    color("seagreen") box();
    mock_box_parts();
    translate([0, 0, 55]) {
        color("ghostwhite", 0.5) translate([0, 0, od]) lid_inplace();
        mock_lid_parts();
        for (p = [dial1, dial2]) color("dimgray") translate([p[0], p[1], od + lid_t + 4]) knob();
    }
    color("orange") translate([ow/2 - clip_w/2, oh - clip_below, -12]) multmatrix([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1]]) clip();
}
