# Cubenect
Cubenect is a large cube with a canvas wrapped around it that works as a multitouch Kinect-based computer interface. The Cubenect project is currently an exhibit at a [digital exhibition](https://digitaliseromu.hu/) in Hungary. See the article on [index.hu](https://index.hu/kultur/2021/09/18/ozd-kohaszat-digitalis-eromu-mars-interaktiv-szeleczky-zita-jovo/) if you are interested (language is hungarian).

![cubenect (6)](https://user-images.githubusercontent.com/20257264/110841923-c5d22e00-82a6-11eb-8527-c66b61510058.gif)

## How it works

The side of the cube is projected from inside with a special projector creating the view. Inside the cube a Kinect is hanged right at the middle of the opposite side and tilted in 90 degrees. For processing a low-cost PC is used which is also placed inside the cube.

The Cubenect software only uses the Kinect's depth image. Using an adaptive threshold based algorithm, the software detects the contacts that have been made with the canvas and a custom tracking algorithm tracks these through their lifetime (until we stop pushing the canvas). The software registers and sends an update on each contact creation/change as a multitouch event through the [Virtual touchscreen](https://github.com/vi/virtual_touchscreen) driver to the underlying operating system.

The repository also contains a calibration program with which the Kinect-based touchscreen and the projector's display can be calibrated.

Eventually the result is a fully functional multitouch screen on the side of the cube. In the demo, we used the amazing fluid simulator by [PavelDoGreat](https://github.com/PavelDoGreat/WebGL-Fluid-Simulation) in fullscreen mode from a Chromium browser (only modifications to the simulator was just the removal of the menu bar).


## Installation

This installation guide is used to get a system up and running as fast as possible with the capabilities and content of the actual exhibit. It will configure your Ubuntu operating system so its almost like in Kiosk mode. That means at startup it will automatically run a fullscreen Chromium instance with the fluid simulator and start Cubenect tracking. It will also automatically calibrate the Kinect to the depth of the canvas thus ignoring misalignments happened to the kinect or the cube while being powered off and/or moved elsewhere.

The installation have been intentionally made very simple (however this phase could be improved a lot). Therefore a complete reinstall can be made by even a non-professional on site with following some simple instructions, in case of unexpected failure or system meltdown.

*Note: For the installation you don't need a Kinect or a GPU.*

### 1. Install Ubuntu

In order to install Cubenect as simply as possible we need a new Ubuntu 20.04 LTS installation on our system.

1. Create an ubuntu installer:
    - Download [Rufus](https://rufus.ie) and [Ubuntu 20.04 LTS Desktop image](https://releases.ubuntu.com/20.04/)
    - Configure a pendrive as an installer for Ubuntu with Rufus
2. Install Ubuntu
    - Your name: **digital**
    - Your computer's name: **digital**
    - password: **1234** (can be anything else)

### 2. (opt.) Update Nvidia drivers

It is recommended to use a GPU for the WebGL fluid simulator in case of a low-end CPU. Even the cheapest GPU can make a huge difference. At the exhibition we are using an *Nvidia GT 1030* low-end GPU and it's more than enough for this job. However for it to run smoothly, the drivers needs to be updated.

1. In Ubuntu press **Super Key + A** (*Super* is the equivalent of the *Windows Key* in Windows or the *Command Key* in macOS)
2. Search for **Software & Update** and open it
3. Go to the **Additional Drivers** tab
4. Select the first Nvidia driver that is **proprietary** and **tested**
5. Press **apply changes**
6. **Restart** the computer

### 3. Install Cubenect and configure system

Note: *in the terminal, you might need to enter your password ('1234' - by default) at certain stages.*

1. press **Ctrl+Alt+T** to open a terminal.
2. Type and run: `sudo apt-get update`
3. Type and run: `sudo apt-get install -y git`
4. Type and run: `git clone https://github.com/gaborpelesz/cubenect ~/cubenect`
5. Type and run: `chmod +x ~/cubenect/install.sh`
6. Type and run: `~/cubenect/install.sh`
7. (opt) Calibrate cubenect or add previous calibration file
7. **Restart** the computer

After restarting everything should be set and the computer should startup in the "Exhibition" mode.

## Usage

### Wait ~20 seconds after Fluid simulator has started

After the system boots up and you see the Fluid simulator initialize (it starts with random blows of fluids), you should wait approximately **20 seconds**. There is a 10 seconds delay added to the start of the Cubenect software (so dependencies can load before) and it should take approximately 10 seconds to the software to start and do its initial calibration.

**WARNING:** Do **NOT** touch the cube's canvas until the 20 seconds have passed because it has a high chance of ruining the calibration. In case of this happening, **Restart** the computer.

### Calibrating Cubenect

At first it is possible that your touch and the resulting action is misaligned. Therefore we created a calibration software to calibrate the touch events to the projectors view.

It is easier to calibrate Cubenect before Restarting the computer after the installation. In that case, to run calibration open up a terminal (**Ctrl+Alt+T**) and type: `python3 ~/cubenect/cubenect/calibrate_cubenect.py`.

**WARNING:** as for now, the calibration assumes a rotated Kinect in 90 degrees clockwise inside the cube (or anti-clockwise if you stand in front of the cameras).

The calibration screen is a fullwhite screen projected where the a touch event is shown as a red circular indicator. The job of the calibrator is to first find the **top-left** most point of the canvas where the Kinect is sensing the touch (the indicator is present somewhere). After finding it the calibrator should leave his finger at this position and proceed to the next phase of the calibration which is to move the indicator red circle with the Arrow keys to the exact point he/she is currently pointing to.

The next step is to do the exact same procedure for the **bottom-right** most point too.

The stages of the calibration procedure (After finishing a step, hit **Enter**):
1. Find **top-left** most point with your finger on the canvas that is still being detected
2. Move the red indicator circle to the exact same point as your finger on the canvas
3. Find **bottom-right** most point with your finger on the canvas that is still being detected
4. Move the red indicator circle to the exact same point as your finger on the canvas

The keyboard inputs for the calibration program:
- `q` -> **exit** and abort the calibration
- `Shift` -> change the indicator circle's **moving speed** (slow, medium, fast)
- `Enter` -> proceed to the **next stage** of the calibration
- `Arrow Keys` -> move the calibration indicator circles

## License

The project is under GPLv3 License, and available for non-commercial purposes.

© Gabor Pelesz 2021, <gaborpelesz@gmail.com>
