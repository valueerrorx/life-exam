import QtQuick 2.0
import QtQuick.Layouts 1.1
import org.kde.plasma.core 2.0 as PlasmaCore

Item {
    id: main

    Layout.minimumWidth: vertical ? 0 : sizehelper.paintedWidth + (units.smallSpacing * 2)
    Layout.maximumWidth: vertical ? Infinity : Layout.minimumWidth
    Layout.preferredWidth: vertical ? undefined : Layout.minimumWidth
    Layout.minimumHeight: vertical ? sizehelper.paintedHeight + (units.smallSpacing * 2) : 0
    Layout.maximumHeight: vertical ? Layout.minimumHeight : Infinity
    Layout.preferredHeight: vertical ? Layout.minimumHeight : theme.mSize(theme.defaultFont).height * 2

    readonly property bool vertical: plasmoid.formFactor == PlasmaCore.Types.Vertical
    property string name: ""

    function updateText() {
        var xhr = new XMLHttpRequest;
        xhr.open("GET", "/home/waldelf/.life/EXAM/EXAMCONFIG/myname.txt");
        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                var response = xhr.responseText;
                //remove linebreaks and other bullshit
                response = response.replace(/(\r\n\t|\n|\r\t)/gm,"");
                main.name = response;
            }
        };
        xhr.send();
    }
    
    Component.onCompleted: {
         updateText()
    }

    Text {
        id: sizehelper

        font.pixelSize: vertical ? theme.mSize(theme.defaultFont).height * 2 : 1024 // random "big enough" size - this is used as a max pixelSize by the fontSizeMode
        minimumPixelSize: theme.mSize(theme.smallestFont).height
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        fontSizeMode: vertical ? Text.HorizontalFit : Text.VerticalFit
        color: "#ffffff"
        wrapMode: Text.NoWrap
        anchors {
            fill: parent
            leftMargin: units.smallSpacing
            rightMargin: units.smallSpacing
        }
        text: "User: " +   main.name 
    }
}
