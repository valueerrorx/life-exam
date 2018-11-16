import QtQuick 2.0
import QtQuick.Layouts 1.1
import org.kde.plasma.plasmoid 2.0

Item {
    id: root
    width: units.gridUnit * 12
    height: units.gridUnit * 4

    Plasmoid.preferredRepresentation: Plasmoid.compactRepresentation

    Plasmoid.compactRepresentation: LifeName { }
    Plasmoid.fullRepresentation: LifeName { }
}
