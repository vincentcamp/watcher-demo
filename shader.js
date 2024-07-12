import * as Shox from "https://cdn.jsdelivr.net/npm/shox@1.1.3/src/Shox.js"

const PI = 3.141592653589793
const TAU = 6.283185307179586

export const UPDATE_VERT = `
	precision mediump float;

	uniform vec2 uMouse;
	uniform float uSpeed;
	uniform float uTime;

	in vec2 aPosition;
	in float aAge;
	in float aLife;
	in vec2 aVel;

	out vec2 vPosition;
	out float vAge;
	out float vLife;
	out vec2 vVel;

	uniform float uScale;

	${Shox.noiseMath}
	${Shox.snoise3D}
	${Shox.snoise3DImage}
	${Shox.hash}
	${Shox.displace}

	vec4 noise(vec2 uv, float scal, float gain, float ofst, float expo, vec3 move) {
		vec4 noise;
		noise  =     1.*snoise3DImage((uv-vec2(421., 132))*1., scal, gain, ofst, expo, move);
		noise +=     .5*snoise3DImage((uv-vec2(913., 687))*2., scal, gain, ofst, expo, move);
		noise +=    .25*snoise3DImage((uv-vec2(834., 724))*4., scal, gain, ofst, expo, move);
		noise +=   .125*snoise3DImage((uv-vec2(125., 209))*8., scal, gain, ofst, expo, move);
		noise +=  .0625*snoise3DImage((uv-vec2(387., 99))*16., scal, gain, ofst, expo, move);
		noise /= 1.9375;
		return noise;
	}

	void main() {
		float scal = 5.;
		float gain = 2.;
		float ofst = .5;
		float expo = 2.;
		vec3  move = vec3(0., 0., uTime*.25);
		vec4 dimg = noise(aPosition/vec2(1., uScale), scal, gain, ofst, expo, move);

		vec2 noise = dimg.rg;

		vec2 force = 3.*(2.*noise.rg-1.);

		if (aAge >= aLife) {
			vPosition = vec2(gl_VertexID%80, gl_VertexID/80)/vec2(80.-1.);
			vPosition = 2.*vPosition-1.;
			vPosition = 2.*hash22(vPosition*314159.26)-1.;

			vPosition = uMouse;
			vAge = 0.;
			vLife = aLife;
			vVel = .95*aVel+uSpeed*force*.016*.5;
		} else {
			vPosition = aPosition+aVel*.016;
			vAge = aAge+.016;
			vLife = aLife;
			vVel = .95*aVel+uSpeed*force*.016*.5;
		}
	}
`

export const UPDATE_FRAG = `
	precision mediump float;
	void main() { discard; }
`

export const RENDER_VERT = `
	precision mediump float;

	in vec2 aPosition;
	in float aAge;
	in float aLife;
	in vec2 aCoord;
	in vec2 aTexCoord;

	out float vAge;
	out float vLife;
	out vec2 vTexCoord;

	uniform float uScale;

	void main() {
		float t = aAge/aLife;
		vAge = aAge;
		vLife = aLife;
		vTexCoord = aTexCoord;

		float tc = .5+.5*cos(2.*${PI}*t-${PI});
		float ti = 1.-t;
		gl_Position = vec4(aPosition+ti*.05*aCoord*vec2(1., uScale), 0., 1.);
	}
`

export const RENDER_FRAG = `
	precision mediump float;

	uniform sampler2D uSprite;

	in float vAge;
	in float vLife;
	in vec2 vTexCoord;

	out vec4 fragColor;

	float circle(vec2 uv, vec2 pos, float r, float blur) {
		return smoothstep(blur, -blur, length(uv-pos)-r);
	}

	void main() {
		vec2 uv = vTexCoord;
		float t =  vAge/vLife;
		float tc = .5+.5*cos(${TAU}*t-${PI});
		float ti = 1.-t;

		float cir = circle(uv, vec2(.5), .1, .1);
		vec4 color;
		color.rgb = vec3(1., .8, .3);
		// color.a = tc;
		color.a = ti;

		fragColor = color * cir;
	}
`
