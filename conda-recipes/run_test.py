import os
import sys

# # Disable MaBoSS (critical for Windows CI stability)
# if  sys.platform.startswith("win"):
#     os.environ["CC3D_DISABLE_MABOSS"] = "1"

print("Testing CC3D Player5 import...")

try:
    import cc3d
    import cc3d.player5
    print("cc3d.player5 import OK")
except Exception as e:
    print("Import failed:", e)
    sys.exit(1)

print("CC3D Player5 basic test passed")
sys.exit(0)
