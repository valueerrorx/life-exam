import QtQuick 2.0
import org.kde.plasma.components 2.0 as PlasmaComponents
import org.kde.plasma.plasmoid 2.0   
import org.kde.plasma.core 2.0 as PlasmaCore

Item {
    id: main
    property string name: ""

    function updateText() {
        var xhr = new XMLHttpRequest;
        xhr.open("GET", "/home/student/.life/EXAM/EXAMCONFIG/myname.txt");
        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                var response = xhr.responseText;
       
                console.log(response);
                main.name = response;
              
            }
        };
        xhr.send();
    }
    
    Component.onCompleted: {
        updateText()
    }
    
    PlasmaComponents.Label {
        text: " " +main.name;
    }
    
    
}

