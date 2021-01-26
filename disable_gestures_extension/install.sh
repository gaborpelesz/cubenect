mkdir -p ~/.local/share/gnome-shell/extensions/disable-gestures@cubenect
cp -r ~/cubenect/disable_gestures_extension/src/* ~/.local/share/gnome-shell/extensions/disable-gestures@cubenect
gnome-extensions enable disable-gestures@cubenect
