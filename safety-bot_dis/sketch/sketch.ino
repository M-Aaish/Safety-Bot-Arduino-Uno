// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

#include <Arduino_RouterBridge.h>

// --- MOTOR 1 PINS ---
int RPWM1 = 5;
int LPWM1 = 6;
int L_EN1 = 7;
int R_EN1 = 8;

// --- MOTOR 2 PINS ---
int RPWM2 = 10;
int LPWM2 = 2;
int L_EN2 = 3; 
int R_EN2 = 9;

int mspeed = 200;

void setup() {
    // Setup Motor 1
    pinMode(RPWM1, OUTPUT);
    pinMode(LPWM1, OUTPUT);
    pinMode(L_EN1, OUTPUT);
    pinMode(R_EN1, OUTPUT);
    digitalWrite(RPWM1, LOW);
    digitalWrite(LPWM1, LOW);
    digitalWrite(L_EN1, LOW);
    digitalWrite(R_EN1, LOW);

    // Setup Motor 2
    pinMode(RPWM2, OUTPUT);
    pinMode(LPWM2, OUTPUT);
    pinMode(L_EN2, OUTPUT);
    pinMode(R_EN2, OUTPUT);
    digitalWrite(RPWM2, LOW);
    digitalWrite(LPWM2, LOW);
    digitalWrite(L_EN2, LOW);
    digitalWrite(R_EN2, LOW);

    Bridge.begin();
    
    // Provide the motor commands to your App Lab code
    Bridge.provide("set_forward", set_forward);
    Bridge.provide("set_reverse", set_reverse);
    Bridge.provide("set_left", set_left);
    Bridge.provide("set_right", set_right);
    Bridge.provide("stop_motor", stop_motor);
}

void loop() {}

void set_forward(bool state) {
    if (state) {
        // Enable both motors
        digitalWrite(R_EN1, HIGH);
        digitalWrite(L_EN1, HIGH);
        analogWrite(LPWM1, 0);

        digitalWrite(R_EN2, HIGH);
        digitalWrite(L_EN2, HIGH);
        analogWrite(LPWM2, 0);

        // Soft start BOTH motors simultaneously going forward
        for(int i = 0; i <= mspeed; i++) {
            analogWrite(RPWM1, i);
            analogWrite(RPWM2, i);
            delay(10);
        }
    } else {
        STOP_INTERNAL();
    }
}

void set_reverse(bool state) {
    if (state) {
        // Enable both motors
        digitalWrite(R_EN1, HIGH);
        digitalWrite(L_EN1, HIGH);
        analogWrite(RPWM1, 0);

        digitalWrite(R_EN2, HIGH);
        digitalWrite(L_EN2, HIGH);
        analogWrite(RPWM2, 0);

        // Soft start BOTH motors simultaneously going reverse
        for(int i = 0; i <= mspeed; i++) {
            analogWrite(LPWM1, i);
            analogWrite(LPWM2, i);
            delay(10);
        }
    } else {
        STOP_INTERNAL();
    }
}

void set_left(bool state) {
    if (state) {
        digitalWrite(R_EN1, HIGH);
        digitalWrite(L_EN1, HIGH);
        analogWrite(RPWM1, 0);

        digitalWrite(R_EN2, HIGH);
        digitalWrite(L_EN2, HIGH);
        analogWrite(LPWM2, 0);

        // Turn LEFT: Motor 1 goes Reverse, Motor 2 goes Forward
        for(int i = 0; i <= mspeed; i++) {
            analogWrite(LPWM1, i); // M1 Reverse
            analogWrite(RPWM2, i); // M2 Forward
            delay(10);
        }
    } else {
        STOP_INTERNAL();
    }
}

void set_right(bool state) {
    if (state) {
        digitalWrite(R_EN1, HIGH);
        digitalWrite(L_EN1, HIGH);
        analogWrite(LPWM1, 0);

        digitalWrite(R_EN2, HIGH);
        digitalWrite(L_EN2, HIGH);
        analogWrite(RPWM2, 0);

        // Turn RIGHT: Motor 1 goes Forward, Motor 2 goes Reverse
        for(int i = 0; i <= mspeed; i++) {
            analogWrite(RPWM1, i); // M1 Forward
            analogWrite(LPWM2, i); // M2 Reverse
            delay(10);
        }
    } else {
        STOP_INTERNAL();
    }
}

void stop_motor(bool state) {
    if (state) {
        STOP_INTERNAL();
    }
}

// Internal helper to stop BOTH motors safely
void STOP_INTERNAL() {
    // Stop Motor 1
    digitalWrite(R_EN1, LOW);
    digitalWrite(L_EN1, LOW);
    analogWrite(LPWM1, 0);
    analogWrite(RPWM1, 0);

    // Stop Motor 2
    digitalWrite(R_EN2, LOW);
    digitalWrite(L_EN2, LOW);
    analogWrite(LPWM2, 0);
    analogWrite(RPWM2, 0);
}