# Cubenect
Cubenect is a cube with a canvas wrapped around that works as a multitouch Kinect-based computer interface. The Cubenect project is currently an exhibit at a [digital exhibition](https://digitaliseromu.hu/) in Hungary.

![cubenect (6)](https://user-images.githubusercontent.com/20257264/110841923-c5d22e00-82a6-11eb-8527-c66b61510058.gif)

## How it works

The side of the cube is projected from inside with a special projector creating the view. Inside the cube a Kinect is hanged right at the middle of the opposite side and tilted in 90 degrees. For processing a low-cost PC is used which is also placed inside the cube.

The Cubenenct software only uses the Kinect's depth image. Using an adaptive threshold based algorithm, the software detects the contacts that have been made with the canvas and a custom tracker algorithm tracks these through their lifetime (until we stop pushing the canvas). The software registers and sends an update on each contact creation and change as a multitouch event through the Virtual touchscreen driver to the Linux system.

The repository also contains a calibration program with which the Kinect-based touchscreen and the projectors display can be calibrated.

Eventually the result is a fully functional multitouch screen on the side of the cube. In the demo, we used the amazing fluid simulator by [PavelDoGreat](https://github.com/PavelDoGreat/WebGL-Fluid-Simulation) in fullscreen mode from a Chromium browser (only modifications to the simulator was just the removal of the menu bar)


## Installation

...

## Usage

...
