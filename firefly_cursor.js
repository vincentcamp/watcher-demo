import * as Shox from "https://cdn.jsdelivr.net/npm/shox@1.1.3/src/Shox.js"
import Olon from "https://cdn.jsdelivr.net/npm/olon@0.2.4/dist/Olon.min.js"
import { UPDATE_VERT, UPDATE_FRAG, RENDER_VERT, RENDER_FRAG } from "./shader.js"
import { random, min } from "./tools.js"

console.log("Firefly cursor script loaded");

const COLS = 80;
const ROWS = 80;
const MAX_AMOUNT = COLS * ROWS;
const MIN_AGE = 0;
const MAX_AGE = 30;
const SPEED = 0.5;
let BORN_AMOUNT = 0;

let ol;

function initFireflyCursor() {
    console.log("Initializing firefly cursor");
    const canvas = document.getElementById('firefly-canvas');
    if (!canvas) {
        console.error("Firefly canvas not found");
        return;
    }
    
    try {
        ol = Olon(canvas);
        console.log("Olon initialized");
    } catch (error) {
        console.error("Error initializing Olon:", error);
        return;
    }

    try {
        ol.blend({ sfactor: ol.SRC_ALPHA, dfactor: ol.ONE });
        ol.enableBlend();
        console.log("Blend mode set");
    } catch (error) {
        console.error("Error setting blend mode:", error);
        return;
    }

    console.log("Creating shader programs");
    const TFV = ["vPosition", "vAge", "vLife", "vVel"];
    let updateProgram, renderProgram;
    try {
        updateProgram = ol.createProgram(UPDATE_VERT, UPDATE_FRAG, TFV);
        renderProgram = ol.createProgram(RENDER_VERT, RENDER_FRAG);
        console.log("Shader programs created successfully");
    } catch (error) {
        console.error("Error creating shader programs:", error);
        return;
    }

    console.log("Setting up attributes and buffers");
    const aPosition = { name: "aPosition", unit: "f32", size: 2 };
    const aAge = { name: "aAge", unit: "f32", size: 1 };
    const aLife = { name: "aLife", unit: "f32", size: 1 };
    const aVel = { name: "aVel", unit: "f32", size: 2 };
    const aCoord = { name: "aCoord", unit: "f32", size: 2 };
    const aTexCoord = { name: "aTexCoord", unit: "f32", size: 2 };

    const updateAttribs = [aPosition, aAge, aLife, aVel];
    const renderAttribs = [aPosition, aAge, aLife];
    const quadAttribs = [aCoord, aTexCoord];

    const particleData = [];
    for (var i = 0; i < MAX_AMOUNT; i++) {
        const LIFE = random(MIN_AGE, MAX_AGE);
        particleData.push(0, 0, LIFE + 1, LIFE, 0, 0);
    }
    const initData = ol.Data(particleData);
    const quadData = ol.quadData();

    let buffer0, buffer1, quadBuffer;
    try {
        buffer0 = ol.createBuffer(initData, ol.STREAM_DRAW);
        buffer1 = ol.createBuffer(initData, ol.STREAM_DRAW);
        quadBuffer = ol.createBuffer(quadData, ol.STATIC_DRAW);
        console.log("Buffers created successfully");
    } catch (error) {
        console.error("Error creating buffers:", error);
        return;
    }

    console.log("Creating VAOs");
    const VAOConfig = (buffer, stride, attributes, divisor) => ({ buffer, stride, attributes, divisor });
    let updateVAO0, updateVAO1, renderVAO0, renderVAO1;
    try {
        updateVAO0 = ol.createVAO(updateProgram, [VAOConfig(buffer0, 4 * 6, updateAttribs)]);
        updateVAO1 = ol.createVAO(updateProgram, [VAOConfig(buffer1, 4 * 6, updateAttribs)]);
        renderVAO0 = ol.createVAO(renderProgram, [
            VAOConfig(buffer0, 4 * 6, renderAttribs, 1),
            VAOConfig(quadBuffer, 4 * 4, quadAttribs),
        ]);
        renderVAO1 = ol.createVAO(renderProgram, [
            VAOConfig(buffer1, 4 * 6, renderAttribs, 1),
            VAOConfig(quadBuffer, 4 * 4, quadAttribs),
        ]);
        console.log("VAOs created successfully");
    } catch (error) {
        console.error("Error creating VAOs:", error);
        return;
    }

    const buffers = [buffer0, buffer1];
    const updateVAOs = [updateVAO0, updateVAO1];
    const renderVAOs = [renderVAO0, renderVAO1];
    let [read, write] = [0, 1];

    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX / window.innerWidth * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight * 2 - 1);
    });

    console.log("Starting render loop");
    ol.render(() => {
        BORN_AMOUNT = min(MAX_AMOUNT, BORN_AMOUNT + 10);

        ol.clearColor(0, 0, 0, 0);
        ol.clearDepth();

        try {
            ol.use({
                program: updateProgram,
            }).run(() => {
                ol.transformFeedback(updateVAOs[read], buffers[write], ol.POINTS, () => {
                    ol.uniform("uMouse", [mouseX, mouseY]);
                    ol.uniform("uSpeed", SPEED);
                    ol.uniform("uTime", ol.frame / 60);
                    ol.uniform("uScale", ol.width / ol.height);
                    ol.points(0, BORN_AMOUNT);
                });
            });

            ol.use({
                VAO: renderVAOs[read],
                program: renderProgram,
            }).run(() => {
                ol.uniform("uScale", ol.width / ol.height);
                ol.trianglesInstanced(0, 6, BORN_AMOUNT);
            });

            [read, write] = [write, read];
        } catch (error) {
            console.error("Error in render loop:", error);
        }
    });

    console.log("Firefly cursor initialized");
}

window.addEventListener('load', () => {
    console.log("Window loaded, initializing firefly cursor");
    initFireflyCursor();
});

window.addEventListener('resize', () => {
    if (ol) {
        console.log("Resizing canvas");
        ol.resize(window.innerWidth, window.innerHeight);
    }
});