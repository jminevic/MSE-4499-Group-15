#ifndef HELPER_H
#define HELPER_H

#include <Arduino.h>
#include <HX711.h>

extern HX711 loadCell;

#define encodeSDA 47
#define encodeSCL 48
#define loadSDA 35
#define loadSCL 36
#define potPin 4
#define flexExtRightPot 5
#define flexExtLeftPot  6

float radialUlnar();
float flexExtLeft();
float flexExtRight();
float proSupF();
float proSupROM();
float pinchTest();

#endif
