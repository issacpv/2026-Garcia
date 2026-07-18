import math

LAYER_HEIGHT = 0.4      # mm per layer
STEPS_PER_MM = 5        # points per mm of circumference
LIFT = 10.0              # mm lifted above the current layer while curing
TRAVEL_F = "4800.000"   # travel feedrate
E_RETRACT = "2.00000"   # retract/unretract amount
FINAL_Z = 50            # final park height


def generate_tube_gcode(diameter, layers, cure_seconds):
    r = diameter / 2.0
    steps = int(round(math.pi * diameter * STEPS_PER_MM))  # 5 steps per mm of circumference
    lines = []

    def out(s):
        lines.append(s)

    def circle_points():
        # start at (-r, 0) and travel clockwise (first point moves toward -Y)
        for i in range(1, steps + 1):
            a = math.pi + i * (2.0 * math.pi / steps)
            x = r * math.cos(a)
            y = r * math.sin(a)
            out(f"G1 X{x:.6f} Y{y:.6f} E1")

    # ---- prime / wipe header (layer 1, Z0) ----
    out(f"G1 Z0 F{TRAVEL_F}")
    out(f"G1 E-{E_RETRACT} F2400.00000")
    out(f"G1 X{-r} Y0.000000 F{TRAVEL_F}")
    out("G4 P0")
    # ---- layers ----
    layer_change_lines = [2]  # line numbers where each layer begins (first entry mirrors the source file)
    park_x, park_y = -36.63, -24.42

    for layer in range(1, layers + 1):
        z = (layer - 1) * LAYER_HEIGHT
        circle_points()

        if layer == layers:
            break

        # lift 1cm, park, cure, return to circle start, drop to next layer
        out(f"G0 Z{z + LIFT:.3f} F{TRAVEL_F}")
        layer_change_lines.append(len(lines) + 1)
        out(f"G0 X{park_x:.2f} Y{park_y:.2f} F{TRAVEL_F}")
        out(f"G4 S{cure_seconds}")
        out(f"G0 X{-r:.3f} Y0.000 F{TRAVEL_F}")
        out(f"G1 Z{z + LAYER_HEIGHT:.3f} F{TRAVEL_F}")
        out("G4 P0")

    # ---- footer ----
    out(f"G1 E-{E_RETRACT} F2400.00000")
    out(f"G0 Z{FINAL_Z}")
    out(f"G0 Z{FINAL_Z}")
    line_count = len(lines)
    out(";alternatingmarkers 0")
    out(f";xmin {r:.6f}")
    out(f";xmax {r:.6f}")
    out(f";ymin {r:.6f}")
    out(f";ymax {r:.6f}")
    out(";zmin 0.000000")
    out(f";zmax {FINAL_Z:.6f}")
    out(";Layer Changes " + " ".join(str(n) for n in layer_change_lines) + " ")
    out(f";Layer Count {layers}")
    out(f";Line Count {line_count}")

    return "\n".join(lines) + "\n"


def main():
    diameter = float(input("Tube diameter (mm): "))
    layers = int(input("Number of layers: "))
    cure_seconds = int(input("Cure time per layer (seconds): "))

    # keep the filename tidy: 24.0 -> "24", 24.5 -> "24.5"
    dia_str = f"{diameter:g}"

    filename = f"C:\\Users\\issac\\Desktop\\2026-Garcia\\!tube{dia_str}x{layers}({cure_seconds}s).pp.gcode"
    out_path = filename                     # current folder (for testing)
    # out_path = "D:\\" + filename          # thumb drive (use this for the printer)

    gcode = generate_tube_gcode(diameter, layers, cure_seconds)
    with open(out_path, "w") as f:
        f.write(gcode)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
