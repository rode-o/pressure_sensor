/***********************************************************************
  SparkFun Qwiic MicroPressure  —  Desktop‑Logger Firmware
  • Reads the MPR‑series pressure sensor (0–25 PSI variant, I²C addr 0x18)
  • Prints one line / 500 ms  →  “counts=0x4A72A1 | P=10.2356 PSI  ( 70.569 kPa)”
    This exact format is what the PyQt6 desktop app parses.
************************************************************************/

#include <Wire.h>

/* ---------- user‑tunable constants --------------------------------- */
const uint8_t  MPR_ADDR      = 0x18;              // I²C address (fixed)
const uint8_t  CMD_CONVERT[] = { 0xAA, 0x00, 0x00 };

const bool     DEBUG_STATUS  = false;             // true = print status byte

/* Transfer‑function constants for ***0–25 PSI*** device.  
   If you use a different range, adjust COUNTS_MIN / MAX & PSI_MAX.      */
const uint32_t COUNTS_MIN    = 0x19999AUL;        // 10 % of 2^24
const uint32_t COUNTS_MAX    = 0xE66666UL;        // 90 % of 2^24
const float    PSI_MAX       = 25.0f;             // full‑scale
const float    KPA_PER_PSI   = 6.894757f;

/* ------------------------------------------------------------------ */
/* waitDRDY – poll status until DRDY (bit 5) clears                    */
/* returns true on success, false on timeout                           */
/* ------------------------------------------------------------------ */
bool waitDRDY(uint16_t tries = 100, uint16_t delay_ms = 5)
{
  for (uint16_t i = 0; i < tries; ++i) {
    Wire.requestFrom(MPR_ADDR, (uint8_t)1);
    if (!Wire.available()) return false;          // I²C fault
    uint8_t stat = Wire.read();
    if (DEBUG_STATUS) {
      Serial.print(F("status byte: 0x"));
      Serial.println(stat, HEX);
    }
    if ((stat & 0x20) == 0) return true;          // DRDY cleared
    delay(delay_ms);
  }
  return false;                                   // timed out
}

/* ------------------------------------------------------------------ */
void setup()
{
  Serial.begin(115200);
  Wire.begin();
  delay(50);

  /* Quick presence test */
  Wire.beginTransmission(MPR_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("Sensor not detected – check SDA/SCL & 3 V supply."));
    while (true);  // halt
  }
  Serial.println(F("# MPR sensor detected – streaming begins…"));
}

/* ------------------------------------------------------------------ */
void loop()
{
  /* 1. Trigger conversion */
  Wire.beginTransmission(MPR_ADDR);
  Wire.write(CMD_CONVERT, sizeof(CMD_CONVERT));
  if (Wire.endTransmission() != 0) {
    Serial.println(F("# I²C error sending convert command"));
    delay(500);
    return;
  }

  /* 2. Wait for new data */
  if (!waitDRDY()) {
    Serial.println(F("# Timeout: DRDY stayed high >500 ms"));
    delay(500);
    return;
  }

  /* 3. Read 24‑bit pressure counts */
  Wire.requestFrom(MPR_ADDR, (uint8_t)4);
  if (Wire.available() != 4) {
    Serial.println(F("# I²C frame read error"));
    delay(500);
    return;
  }
  Wire.read();                                    // status byte (should be 0)
  uint32_t counts = ((uint32_t)Wire.read() << 16) |
                    ((uint32_t)Wire.read() << 8 ) |
                     (uint32_t)Wire.read();

  /* 4. Convert to PSI & kPa */
  float psi = (counts - COUNTS_MIN) * PSI_MAX /
              (COUNTS_MAX - COUNTS_MIN);
  float kPa = psi * KPA_PER_PSI;

  /* 5. Emit one line */
  Serial.print(F("counts=0x")); Serial.print(counts, HEX);
  Serial.print(F(" | P="));     Serial.print(psi, 4);
  Serial.print(F(" PSI  ( "));  Serial.print(kPa, 3);
  Serial.println(F(" kPa)"));

  delay(500);                                   // ≈2 Hz update rate
}
