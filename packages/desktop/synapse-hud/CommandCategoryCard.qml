import QtQuick
import QtQuick.Controls.Basic

Rectangle {
    id: card
    property string title: ""
    property color accentColor: "#cba6f7"
    property var items: []
    property string filterText: ""
    signal itemTriggered(string cmd)

    width: (parent.width - 24) / 3
    height: 236
    radius: 14
    color: "#181825"
    border.color: "#313244"
    border.width: 1

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        // Category Header
        Text {
            text: card.title
            color: card.accentColor
            font { family: "JetBrainsMono Nerd Font"; pixelSize: 11; bold: true; letterSpacing: 0.8 }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: Qt.rgba(card.accentColor.r, card.accentColor.g, card.accentColor.b, 0.3)
        }

        // Action Rows
        Repeater {
            model: card.items
            delegate: Item {
                required property var modelData
                width: parent.width
                height: 32

                readonly property bool matches: {
                    if (card.filterText.trim() === "") return true
                    var q = card.filterText.toLowerCase()
                    return modelData.label.toLowerCase().indexOf(q) !== -1 ||
                           modelData.desc.toLowerCase().indexOf(q) !== -1 ||
                           modelData.key.toLowerCase().indexOf(q) !== -1
                }

                visible: matches

                Rectangle {
                    id: tile
                    anchors.fill: parent
                    radius: 8
                    color: rowMouse.containsMouse ? "#313244" : "transparent"

                    Row {
                        anchors.fill: parent
                        anchors.margins: 6
                        spacing: 8

                        // Key badge chip
                        Rectangle {
                            width: 22
                            height: 20
                            radius: 5
                            color: rowMouse.containsMouse ? card.accentColor : "#11111b"
                            border.color: card.accentColor
                            border.width: 1
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: modelData.key
                                color: rowMouse.containsMouse ? "#11111b" : card.accentColor
                                font { family: "JetBrainsMono Nerd Font"; pixelSize: 10; bold: true }
                                anchors.centerIn: parent
                            }
                        }

                        // Label
                        Text {
                            text: modelData.label
                            color: rowMouse.containsMouse ? "#ffffff" : "#cdd6f4"
                            font { family: "JetBrainsMono Nerd Font"; pixelSize: 11; bold: true }
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        // Desc
                        Text {
                            text: "· " + modelData.desc
                            color: "#6c7086"
                            font { family: "JetBrainsMono Nerd Font"; pixelSize: 10 }
                            anchors.verticalCenter: parent.verticalCenter
                            elide: Text.ElideRight
                        }
                    }

                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: card.itemTriggered(modelData.cmd)
                    }
                }
            }
        }
    }
}
