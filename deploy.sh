DIR="/home/pi/.kodi/addons/plugin.video.okino.tv/"
if [ ! -d "$DIR" ]
then
 mkdir "$DIR"
 mkdir "$DIR/resources/"
fi
cp okino.py "$DIR"
cp icon.png "$DIR"
cp default.py "$DIR"
cp addon.xml "$DIR"
cp resources/settings.xml "$DIR/resources"
