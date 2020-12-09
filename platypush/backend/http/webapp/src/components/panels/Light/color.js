export class ColorConverter {
    constructor(ranges) {
        this.ranges = {
            hue: [0, 360],
            sat: [0, 100],
            bri: [0, 100],
            ct: [154, 500],
        }

        if (ranges)
            for (const attr of Object.keys(this.ranges))
                if (ranges[attr])
                    this.ranges[attr] = ranges[attr]
    }

    normalize(x, xRange, yRange) {
        return yRange[0] + (((x-xRange[0]) * (yRange[1]-yRange[0])) / (xRange[1]-xRange[0]))
    }

    hslToRgb(h, s, l) {
        [h, s, l] = [
            this.normalize(h, this.ranges.hue, [0, 360]),
            this.normalize(s, this.ranges.sat, [0, 100]),
            this.normalize(l, this.ranges.bri, [0, 100]),
        ]

        l /= 100
        const a = s * Math.min(l, 1 - l) / 100
        const f = n => {
            const k = (n + h / 30) % 12
            const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
            return Math.round(255 * color)
        }

        return [f(0), f(8), f(4)]
    }

    rgbToHsl(r, g, b){
        r /= 255
        g /= 255
        b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if(max === min){
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

            switch(max){
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }

        return [
            parseInt(this.normalize(h, [0, 1], this.ranges.hue)),
            parseInt(this.normalize(s, [0, 1], this.ranges.sat)),
            parseInt(this.normalize(l, [0, 1], this.ranges.bri)),
        ]
    }

    xyToRgb(x, y, brightness) {
        // Set to maximum brightness if no custom value was given (Not the slick ECMAScript 6 way for compatibility reasons)
        if (brightness == null)
            brightness = this.ranges.bri[1];

        const z = 1.0 - x - y;
        const Y = (brightness / (this.ranges.bri[1]-1)).toFixed(2);
        const X = (Y / y) * x;
        const Z = (Y / y) * z;

        //Convert to RGB using Wide RGB D65 conversion
        let red 	=  X * 1.656492 - Y * 0.354851 - Z * 0.255038;
        let green   = -X * 0.707196 + Y * 1.655397 + Z * 0.036152;
        let blue 	=  X * 0.051713 - Y * 0.121364 + Z * 1.011530;

        //If red, green or blue is larger than 1.0 set it back to the maximum of 1.0
        if (red > blue && red > green && red > 1.0) {
            green = green / red;
            blue = blue / red;
            red = 1.0;
        } else if (green > blue && green > red && green > 1.0) {
            red = red / green;
            blue = blue / green;
            green = 1.0;
        } else if (blue > red && blue > green && blue > 1.0) {
            red = red / blue;
            green = green / blue;
            blue = 1.0;
        }

        //Reverse gamma correction
        red 	= red <= 0.0031308 ? 12.92 * red : (1.0 + 0.055) * Math.pow(red, (1.0 / 2.4)) - 0.055;
        green 	= green <= 0.0031308 ? 12.92 * green : (1.0 + 0.055) * Math.pow(green, (1.0 / 2.4)) - 0.055;
        blue 	= blue <= 0.0031308 ? 12.92 * blue : (1.0 + 0.055) * Math.pow(blue, (1.0 / 2.4)) - 0.055;

        //Convert normalized decimal to decimal
        red 	= Math.round(red * 255);
        green 	= Math.round(green * 255);
        blue 	= Math.round(blue * 255);

        if (isNaN(red))
            red = 0;
        if (isNaN(green))
            green = 0;
        if (isNaN(blue))
            blue = 0;

        return [red, green, blue].map((c) => Math.min(Math.max(0, c), 255))
    }

    rgbToXY(red, green, blue) {
        if (red > 1) { red /= 255; }
        if (green > 1) { green /= 255; }
        if (blue > 1) { blue /= 255; }

        //Apply a gamma correction to the RGB values, which makes the color more vivid and more the like the color displayed on the screen of your device
        red 	= (red > 0.04045) ? Math.pow((red + 0.055) / (1.0 + 0.055), 2.4) : (red / 12.92);
        green 	= (green > 0.04045) ? Math.pow((green + 0.055) / (1.0 + 0.055), 2.4) : (green / 12.92);
        blue 	= (blue > 0.04045) ? Math.pow((blue + 0.055) / (1.0 + 0.055), 2.4) : (blue / 12.92);

        //RGB values to XYZ using the Wide RGB D65 conversion formula
        const X 		= red * 0.664511 + green * 0.154324 + blue * 0.162028;
        const Y 		= red * 0.283881 + green * 0.668433 + blue * 0.047685;
        const Z 		= red * 0.000088 + green * 0.072310 + blue * 0.986039;

        //Calculate the xy values from the XYZ values
        let x 		= parseFloat((X / (X + Y + Z)).toFixed(4));
        let y 		= parseFloat((Y / (X + Y + Z)).toFixed(4));

        if (isNaN(x))
            x = 0;
        if (isNaN(y))
            y = 0;

        return [x, y];
    }

    rgbToBri(red, green, blue) {
        return Math.min(2 * this.rgbToHsl(red, green, blue)[2], this.ranges.bri[1])
    }

    getRGB(color) {
        if (color.red != null && color.green != null && color.blue != null)
            return [color.red, color.green, color.blue]
        if (color.r != null && color.g != null && color.b != null)
            return [color.r, color.g, color.b]
        if (color.rgb)
            return color.rgb
    }

    getXY(color) {
        if (color.x != null && color.y != null)
            return [color.x, color.y]
        if (color.xy)
            return color.xy
    }

    toRGB(color) {
        const rgb = this.getRGB(color)
        if (rgb)
            return rgb

        const xy = this.getXY(color)
        if (xy && color.bri)
            return this.xyToRgb(...xy, color.bri)
        if (color.hue && color.sat && color.bri)
            return this.hslToRgb(color.hue, color.sat, color.bri)

        console.debug('Could not determine color space')
        console.debug(color)
    }

    toXY(color) {
        const xy = this.getXY(color)
        if (xy && color.bri)
            return [xy[0], xy[1], color.bri]

        const rgb = this.getRGB(color)
        if (rgb)
            return this.rgbToXY(...rgb)

        if (color.hue && color.sat && color.bri) {
            const rgb = this.hslToRgb(color.hue, color.sat, color.bri)
            return this.rgbToXY(...rgb)
        }

        console.debug('Could not determine color space')
        console.debug(color)
    }

    toHSL(color) {
        if (color.hue && color.sat && color.bri)
            return [color.hue, color.sat, color.bri]

        const rgb = this.getRGB(color)
        if (rgb)
            return this.rgbToHsl(...rgb)

        const xy = this.getXY(color)
        if (xy && color.bri) {
            const rgb = this.xyToRgb(...xy, color.bri)
            return this.rgbToHsl(...rgb)
        }

        console.debug('Could not determine color space')
        console.debug(color)
    }
}
