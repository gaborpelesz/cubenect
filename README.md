# Cubenect
Cubenect is a large cube with a canvas wrapped around it that works as a multitouch Kinect-based computer interface. The Cubenect project is currently an exhibit at a [digital exhibition](https://digitaliseromu.hu/) in Hungary.

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

1. press **Ctrl+Alt+T** to open a terminal. After typing any command you should hit **Enter** to run it.
2. Type: `sudo apt-get update`
3. Type: `sudo apt-get install -y git`
4. Type: `git clone https://github.com/gaborpelesz/cubenect ~/cubenect`
5. Type: `chmod +x ~/cubenect/install.sh`
6. Type: `~/cubenect/install.sh`
7. **Restart** the computer

After restarting everything should be set and the computer should startup in the "Exhibition" mode.

## Usage

### Wait ~20 seconds after Fluid simulator has started

After the system boots up and you see the Fluid simulator initialize (it starts with random blows of fluids), you should wait approximately **20 seconds**. There is a 10 seconds delay added to the start of the Cubenect software (so dependencies can load before) and it should take approximately 10 seconds to the software to start and do its initial calibration.

**WARNING:** Do **NOT** touch the cube's canvas until the 20 seconds have passed because it has a high chance of ruining the calibration. In case of this happening, **Restart** the computer.

### Calibrating Cubenect

At first it is possible that your touch and the resulting action is misaligned. Therefore we created a calibration software to calibrate the touch events to the projectors view.
