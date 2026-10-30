// SynapseOS -- SDDM greeter (Qt6)
// Right-aligned clock + system readout, and a chamfered login panel whose border
// carries two travelling light trails. Every glow follows the theme variant
// (config "variant", e.g. monolith-mauve), which `synapse-theme --sync-greeter` sets.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Shapes
import QtQuick.Effects

Item {
    id: root
    width: 1920
    height: 1080

    // Layout is authored at 1376x768 (the wallpaper size) and scaled by height.
    readonly property real s: height / 768

    readonly property var accents: ({
        mauve: "#cba6f7", tungsten: "#fab387", crimson: "#f38ba8",
        sapphire: "#74c7ec", emerald: "#a6e3a1"
    })
    readonly property string variant: config.stringValue("variant") !== "" ? config.stringValue("variant") : "monolith-mauve"
    readonly property color accent: accents[variant.split("-").pop()] || accents.mauve
    readonly property color text: "#cdd6f4"
    readonly property color subtext: "#a6adc8"
    readonly property color muted: "#9399b2"
    readonly property string mono: "JetBrainsMono Nerd Font"
    readonly property bool animate: config.stringValue("animations") !== "false"
    readonly property string wallDir: config.stringValue("backgrounds") !== "" ? config.stringValue("backgrounds") : "/usr/share/backgrounds/synapseos"

    property string userName: config.stringValue("user") !== "" ? config.stringValue("user") : userModel.lastUser
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property bool busy: false
    property date now: new Date()

    function withAlpha(c, a) { return Qt.rgba(c.r, c.g, c.b, a) }

    function doLogin() {
        if (busy)
            return
        busy = true
        status.show("authenticating…", accent)
        sddm.login(userName, password.text, sessionIndex)
    }

    // No remembered user (fresh install): fall back to the first account.
    Repeater {
        model: userModel
        delegate: Item {
            required property int index
            required property string name
            Component.onCompleted: if (root.userName === "" && index === 0) root.userName = name
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            status.show("authentication failed — try again", "#f38ba8")
            shake.restart()
            password.forceActiveFocus()
        }
        function onLoginSucceeded() {
            status.show("welcome", root.accent)
            outro.start()
        }
    }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

    focus: true
    Keys.onPressed: function(event) {
        var n = event.key - Qt.Key_F2
        if (n >= 0 && n < sessionModel.rowCount()) {
            root.sessionIndex = n
            event.accepted = true
        }
    }

    Rectangle { anchors.fill: parent; color: "#09090d" }

    Image {
        id: wallpaper
        anchors.fill: parent
        source: "file://" + root.wallDir + "/synapse-" + root.variant + ".jpg"
        fillMode: Image.PreserveAspectCrop
        smooth: true
        mipmap: true
        onStatusChanged: if (status === Image.Error) source = "file://" + root.wallDir + "/synapse-monolith-mauve.jpg"
    }

    // --- Clock + readout (right aligned) ---------------------------------
    Column {
        anchors { top: parent.top; right: parent.right; topMargin: 44 * root.s; rightMargin: 48 * root.s }
        width: 300 * root.s
        spacing: 10 * root.s

        Text {
            anchors.right: parent.right
            text: "SYNAPSE"
            color: root.accent
            font { family: root.mono; pixelSize: 11 * root.s; letterSpacing: 5.5 * root.s }
        }
        Text {
            anchors.right: parent.right
            text: Qt.formatTime(root.now, "hh:mm")
            color: root.text
            font { family: root.mono; pixelSize: 68 * root.s; weight: Font.Light }
        }
        Text {
            anchors.right: parent.right
            text: Qt.formatDate(root.now, "ddd · dd MMM yyyy").toUpperCase()
            color: root.subtext
            font { family: root.mono; pixelSize: 12 * root.s; letterSpacing: 1.2 * root.s }
        }
        Rectangle { width: parent.width; height: 1; color: root.withAlpha(root.accent, 0.45) }
        Column {
            width: parent.width
            spacing: 8 * root.s
            Repeater {
                model: [
                    ["HOST", sddm.hostName, false],
                    ["KERNEL", "linux-cachyos · BORE", false],
                    ["DNS", "Quad9 · DNS-over-TLS", false],
                    ["MAC", "randomized", true],
                    ["FIREWALL", "drop inbound", false],
                    ["LOCAL LLM", "ollama", false]
                ]
                delegate: Item {
                    required property var modelData
                    width: 300 * root.s
                    height: 16 * root.s
                    Text { text: modelData[0]; color: root.muted; font { family: root.mono; pixelSize: 11 * root.s } }
                    Text {
                        anchors.right: parent.right
                        text: modelData[1]
                        color: modelData[2] ? root.accent : root.text
                        font { family: root.mono; pixelSize: 11 * root.s }
                    }
                }
            }
        }
    }

    // --- Circuit leads either side of the panel ---------------------------
    Repeater {
        model: [ { x: 280, dir: -1 }, { x: 946, dir: 1 } ]
        delegate: Item {
            required property var modelData
            x: (root.width - 1376 * root.s) / 2 + modelData.x * root.s
            y: panel.y + 141 * root.s
            width: 150 * root.s
            height: 2 * root.s
            Rectangle { anchors.fill: parent; color: root.withAlpha(root.accent, 0.3) }
            Rectangle {
                id: pulse
                width: 48 * root.s; height: parent.height
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.45; color: root.accent }
                    GradientStop { position: 0.5; color: "#ffffff" }
                    GradientStop { position: 0.55; color: root.accent }
                    GradientStop { position: 1.0; color: "transparent" }
                }
                NumberAnimation on x {
                    running: root.animate
                    loops: Animation.Infinite
                    duration: 2600
                    from: modelData.dir > 0 ? -48 * root.s : 150 * root.s
                    to: modelData.dir > 0 ? 150 * root.s : -48 * root.s
                }
            }
            Rectangle {
                width: 10 * root.s; height: 10 * root.s
                x: modelData.dir > 0 ? parent.width - 2 * root.s : -8 * root.s
                y: -4 * root.s
                color: "#09090d"
                border { color: root.accent; width: 2 * root.s }
                SequentialAnimation on opacity {
                    running: root.animate
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.55; duration: 1300; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 1300; easing.type: Easing.InOutSine }
                }
            }
        }
    }

    // --- Login panel ------------------------------------------------------
    Item {
        id: panel
        readonly property real c: 17 * root.s          // chamfer
        readonly property real pad: 24 * root.s        // room for the glow
        width: 520 * root.s
        height: 262 * root.s
        x: (root.width - width) / 2 + shakeX
        y: root.height * 452 / 768
        property real shakeX: 0

        SequentialAnimation {
            id: shake
            NumberAnimation { target: panel; property: "shakeX"; to: -12 * root.s; duration: 50 }
            NumberAnimation { target: panel; property: "shakeX"; to: 12 * root.s; duration: 80 }
            NumberAnimation { target: panel; property: "shakeX"; to: -6 * root.s; duration: 70 }
            NumberAnimation { target: panel; property: "shakeX"; to: 0; duration: 60 }
        }

        // Body
        Shape {
            anchors.fill: parent
            preferredRendererType: Shape.CurveRenderer
            ShapePath {
                strokeWidth: -1
                fillColor: Qt.rgba(8 / 255, 8 / 255, 12 / 255, 0.88)
                startX: panel.c; startY: 0
                PathLine { x: panel.width; y: 0 }
                PathLine { x: panel.width; y: panel.height - panel.c }
                PathLine { x: panel.width - panel.c; y: panel.height }
                PathLine { x: 0; y: panel.height }
                PathLine { x: 0; y: panel.c }
                PathLine { x: panel.c; y: 0 }
            }
        }

        // Border trails: two dashes travelling round the chamfered outline.
        Shape {
            id: trails
            x: -panel.pad; y: -panel.pad
            width: panel.width + 2 * panel.pad
            height: panel.height + 2 * panel.pad
            readonly property real sw: 2.5 * root.s
            // Perimeter of the chamfered rectangle, in stroke-width units (dash units).
            readonly property real perim: (2 * (panel.width + panel.height) - 4 * panel.c + 2 * Math.SQRT2 * panel.c) / sw
            property real offset: 0
            NumberAnimation on offset {
                running: root.animate
                loops: Animation.Infinite
                from: trails.perim; to: 0
                duration: 7000
            }
            ShapePath {   // faint resting outline
                strokeColor: root.withAlpha(root.accent, 0.25)
                strokeWidth: trails.sw
                fillColor: "transparent"
                joinStyle: ShapePath.MiterJoin
                startX: panel.pad + panel.c; startY: panel.pad
                PathLine { x: panel.pad + panel.width; y: panel.pad }
                PathLine { x: panel.pad + panel.width; y: panel.pad + panel.height - panel.c }
                PathLine { x: panel.pad + panel.width - panel.c; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.c }
                PathLine { x: panel.pad + panel.c; y: panel.pad }
            }
            ShapePath {   // accent trails
                strokeColor: root.accent
                strokeWidth: trails.sw
                fillColor: "transparent"
                capStyle: ShapePath.RoundCap
                strokeStyle: ShapePath.DashLine
                dashPattern: [trails.perim * 0.14, trails.perim * 0.36]
                dashOffset: trails.offset
                startX: panel.pad + panel.c; startY: panel.pad
                PathLine { x: panel.pad + panel.width; y: panel.pad }
                PathLine { x: panel.pad + panel.width; y: panel.pad + panel.height - panel.c }
                PathLine { x: panel.pad + panel.width - panel.c; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.c }
                PathLine { x: panel.pad + panel.c; y: panel.pad }
            }
            ShapePath {   // white-hot heads
                strokeColor: "#ffffff"
                strokeWidth: trails.sw
                fillColor: "transparent"
                capStyle: ShapePath.RoundCap
                strokeStyle: ShapePath.DashLine
                dashPattern: [trails.perim * 0.025, trails.perim * 0.475]
                dashOffset: trails.offset - trails.perim * 0.115
                startX: panel.pad + panel.c; startY: panel.pad
                PathLine { x: panel.pad + panel.width; y: panel.pad }
                PathLine { x: panel.pad + panel.width; y: panel.pad + panel.height - panel.c }
                PathLine { x: panel.pad + panel.width - panel.c; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.height }
                PathLine { x: panel.pad; y: panel.pad + panel.c }
                PathLine { x: panel.pad + panel.c; y: panel.pad }
            }
        }
        MultiEffect {   // bloom around the trails
            source: trails
            anchors.fill: trails
            blurEnabled: true
            blurMax: 32
            blur: 0.8
            brightness: 0.45
            z: -1
            SequentialAnimation on opacity {
                running: root.animate
                loops: Animation.Infinite
                NumberAnimation { from: 0.5; to: 1.0; duration: 1750; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.0; to: 0.5; duration: 1750; easing.type: Easing.InOutSine }
            }
        }

        Column {
            anchors { fill: parent; topMargin: 0; leftMargin: 22 * root.s; rightMargin: 18 * root.s }
            spacing: 3 * root.s

            Item {
                width: parent.width; height: 30 * root.s
                Text { anchors.verticalCenter: parent.verticalCenter; x: 2 * root.s; text: "synapseos — tty7"; color: root.subtext; font { family: root.mono; pixelSize: 11 * root.s } }
                Text { anchors { verticalCenter: parent.verticalCenter; right: parent.right } text: "● auth gate"; color: root.accent; font { family: root.mono; pixelSize: 11 * root.s } }
                Rectangle { anchors.bottom: parent.bottom; x: -22 * root.s; width: panel.width; height: 1; color: root.withAlpha(root.accent, 0.45) }
            }
            Item { width: 1; height: 8 * root.s }

            Repeater {
                model: [
                    ["", "SynapseOS 0.1.0-alpha · linux-cachyos BORE (tty7)"],
                    ["[&nbsp;&nbsp;OK&nbsp;&nbsp;]&nbsp;", "Reached target Graphical Interface."],
                    ["[&nbsp;&nbsp;OK&nbsp;&nbsp;]&nbsp;", "Started Synapse AI gateway on 127.0.0.1:8000."],
                    ["[&nbsp;&nbsp;OK&nbsp;&nbsp;]&nbsp;", "Resolver: Quad9 over TLS · MAC randomized."]
                ]
                delegate: Text {
                    required property var modelData
                    required property int index
                    textFormat: Text.StyledText
                    text: "<font color='" + root.accent + "'>" + modelData[0] + "</font>" + modelData[1]
                    color: index === 0 ? root.subtext : root.text
                    font { family: root.mono; pixelSize: 12.5 * root.s }
                    opacity: root.animate ? 0 : 1
                    SequentialAnimation on opacity {
                        running: root.animate
                        PauseAnimation { duration: 200 + 500 * index }
                        NumberAnimation { to: 1; duration: 450; easing.type: Easing.OutCubic }
                    }
                }
            }
            Item { width: 1; height: 6 * root.s }
            Text {
                textFormat: Text.StyledText
                text: "synapseos login: <font color='" + root.accent + "'>" + root.userName + "</font>"
                color: root.text
                font { family: root.mono; pixelSize: 12.5 * root.s }
            }

            Row {
                width: parent.width
                height: 44 * root.s
                spacing: 10 * root.s
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "password:"
                    color: root.text
                    font { family: root.mono; pixelSize: 12.5 * root.s }
                }
                TextField {
                    id: password
                    width: parent.width - 10 * root.s * 2 - enter.width - 80 * root.s
                    height: parent.height
                    echoMode: TextInput.Password
                    passwordCharacter: "•"
                    placeholderText: "enter passphrase"
                    placeholderTextColor: "#7f849c"
                    color: root.accent
                    selectionColor: root.withAlpha(root.accent, 0.4)
                    font { family: root.mono; pixelSize: 14 * root.s }
                    enabled: !root.busy
                    focus: true
                    Accessible.name: "Password for " + root.userName
                    background: Rectangle {
                        color: "transparent"
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: root.withAlpha(root.accent, 0.55) }
                    }
                    onAccepted: root.doLogin()
                    onTextEdited: status.show(keyboard.capsLock ? "caps lock is on" : "", root.subtext)
                }
                Button {
                    id: enter
                    width: 96 * root.s
                    height: parent.height
                    text: "ENTER ↵"
                    enabled: !root.busy
                    onClicked: root.doLogin()
                    contentItem: Text { text: enter.text; color: root.accent; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font { family: root.mono; pixelSize: 12 * root.s; letterSpacing: 1 * root.s } }
                    background: Rectangle { color: root.withAlpha(root.accent, enter.down ? 0.3 : 0.12); border { color: root.accent; width: 1 } }
                }
            }

            Text {
                id: status
                function show(msg, col) { text = msg; color = col }
                height: 16 * root.s
                text: keyboard.capsLock ? "caps lock is on" : ""
                color: root.subtext
                font { family: root.mono; pixelSize: 11 * root.s }
            }

            Item {
                width: parent.width
                height: 44 * root.s
                Row {
                    spacing: 8 * root.s
                    Repeater {
                        model: sessionModel
                        delegate: Button {
                            id: sessionButton
                            required property int index
                            required property string name
                            visible: index < 4
                            height: 40 * root.s
                            text: "[F" + (index + 2) + "] " + name.toLowerCase().replace(/ \(.*\)$/, "")
                            onClicked: root.sessionIndex = index
                            Accessible.name: "Session " + name
                            contentItem: Text { text: sessionButton.text; color: index === root.sessionIndex ? root.text : root.subtext; verticalAlignment: Text.AlignVCenter; font { family: root.mono; pixelSize: 11 * root.s } }
                            background: Rectangle { color: "transparent"; border { width: 1; color: index === root.sessionIndex ? root.accent : "#45475a" } }
                            leftPadding: 10 * root.s; rightPadding: 10 * root.s
                        }
                    }
                }
                Row {
                    anchors.right: parent.right
                    spacing: 4 * root.s
                    Repeater {
                        model: [
                            { label: "restart", can: sddm.canReboot, act: function() { sddm.reboot() } },
                            { label: "shutdown", can: sddm.canPowerOff, act: function() { sddm.powerOff() } }
                        ]
                        delegate: Button {
                            id: powerButton
                            required property var modelData
                            visible: modelData.can
                            height: 40 * root.s
                            text: modelData.label
                            onClicked: modelData.act()
                            contentItem: Text { text: powerButton.text; color: powerButton.hovered ? root.text : root.subtext; verticalAlignment: Text.AlignVCenter; font { family: root.mono; pixelSize: 11 * root.s } }
                            background: Item {}
                            leftPadding: 8 * root.s; rightPadding: 8 * root.s
                        }
                    }
                }
            }
        }
    }

    Text {
        anchors { left: parent.left; bottom: parent.bottom; leftMargin: 28 * root.s; bottomMargin: 26 * root.s }
        text: keyboard.layouts.length > 0 ? keyboard.layouts[keyboard.currentLayout].shortName.toUpperCase() : ""
        color: root.subtext
        font { family: root.mono; pixelSize: 12 * root.s }
    }

    // Fade to black on success so the session start is a clean cut.
    Rectangle {
        id: veil
        anchors.fill: parent
        color: "#09090d"
        opacity: 0
        NumberAnimation on opacity { id: outro; running: false; to: 1; duration: 400 }
    }

    Component.onCompleted: password.forceActiveFocus()
}
