pragma ComponentBehavior: Bound
// SynapseOS Mocha -- SDDM greeter (Qt6)
// Fully procedural Catppuccin Mocha Mauve login screen: no raster background, so
// the greeter renders identically at any resolution and carries no video assets.
// The only way past it is a successful PAM login (sddm.login) or the power buttons.
import QtQuick
import QtQuick.Controls.Basic

Item {
    id: root
    width: 1920
    height: 1080
    focus: true

    readonly property real sx: width / 1920
    readonly property real sy: height / 1080
    readonly property color accent: "#cba6f7"
    readonly property color chrome: "#cdd6f4"
    readonly property color baseBg: "#1e1e2e"
    readonly property color crustBg: "#11111b"
    readonly property color dim: "#a6adc8"
    readonly property string userName: config.stringValue("user") !== "" ? config.stringValue("user") : userModel.lastUser
    property string selectedSession: "xfce.desktop"
    property int xfceSessionIndex: -1
    property int swaySessionIndex: -1
    property int sessionIndex: sessionModel.lastIndex
    property bool busy: false

    function syncSessionIndex() {
        if (selectedSession === "sway.desktop" && swaySessionIndex >= 0) {
            sessionIndex = swaySessionIndex
        } else if (selectedSession === "xfce.desktop" && xfceSessionIndex >= 0) {
            sessionIndex = xfceSessionIndex
        }
    }

    function toggleSession() {
        if (busy)
            return
        selectedSession = (selectedSession === "xfce.desktop") ? "sway.desktop" : "xfce.desktop"
        syncSessionIndex()
        status.show("SESSION: " + (selectedSession === "xfce.desktop" ? "XFCE 4.20 (X11)" : "SWAY (WAYLAND)"), accent)
    }

    function doLogin() {
        if (busy)
            return
        syncSessionIndex()
        busy = true
        status.show("AUTHENTICATING…", accent)
        sddm.login(userName, password.text, sessionIndex)
    }

    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_F2) {
            root.toggleSession()
            event.accepted = true
        }
    }

    // Resolve session indices for xfce.desktop (default) and sway.desktop (Wayland tiling).
    Repeater {
        model: sessionModel
        delegate: Item {
            required property int index
            required property string file
            Component.onCompleted: {
                if (file === "xfce.desktop" || file.endsWith("/xfce.desktop")) {
                    root.xfceSessionIndex = index
                    if (root.selectedSession === "xfce.desktop")
                        root.sessionIndex = index
                } else if (file === "sway.desktop" || file.endsWith("/sway.desktop")) {
                    root.swaySessionIndex = index
                    if (root.selectedSession === "sway.desktop")
                        root.sessionIndex = index
                }
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            status.show("ACCESS DENIED — TRY AGAIN", "#f38ba8")
            shake.restart()
            password.forceActiveFocus()
        }
        function onLoginSucceeded() {
            status.show("WELCOME", accent)
            outro.start()
        }
    }

    // ---------------------------------------------------------------- background
    // Obsidian Crust base with a Catppuccin Base lift toward the centre.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#11111b" }
            GradientStop { position: 0.55; color: "#181825" }
            GradientStop { position: 1.0; color: "#11111b" }
        }
    }

    // Soft mauve bloom behind the emblem, drawn procedurally so it scales cleanly.
    Canvas {
        id: bloom
        readonly property real r: 420 * root.sx
        x: root.width / 2 - r
        y: 300 * root.sy - r
        width: r * 2
        height: r * 2
        onPaint: {
            const ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            const g = ctx.createRadialGradient(r, r, 0, r, r, r)
            g.addColorStop(0.0, "rgba(203,166,247,0.22)")
            g.addColorStop(0.45, "rgba(137,180,250,0.08)")
            g.addColorStop(1.0, "rgba(17,17,27,0.0)")
            ctx.fillStyle = g
            ctx.fillRect(0, 0, width, height)
        }
    }

    // ---------------------------------------------------------------- emblem
    Item {
        id: emblem
        width: 150 * root.sx
        height: width
        x: (root.width - width) / 2
        y: 300 * root.sy - height / 2
        NumberAnimation on opacity { from: 0; to: 1; duration: 1100; easing.type: Easing.OutCubic }

        // Three concentric rings: the synapse node.
        Repeater {
            model: 3
            delegate: Rectangle {
                required property int index
                readonly property real f: 1 - index * 0.28
                width: emblem.width * f
                height: width
                radius: width / 2
                anchors.centerIn: parent
                color: "transparent"
                border.width: Math.max(1, 1.5 * root.sx)
                border.color: index === 0 ? root.accent : (index === 1 ? "#b4befe" : root.chrome)
                opacity: 0.75 - index * 0.18
                SequentialAnimation on scale {
                    loops: Animation.Infinite
                    PauseAnimation { duration: 400 * index }
                    NumberAnimation { to: 1.04; duration: 2200; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 2200; easing.type: Easing.InOutSine }
                }
            }
        }

        // Breathing core
        Canvas {
            id: core
            readonly property real cr: 34 * root.sx
            anchors.centerIn: parent
            width: cr * 2
            height: cr * 2
            onPaint: {
                const ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                const g = ctx.createRadialGradient(cr, cr, 0, cr, cr, cr)
                g.addColorStop(0.0, "rgba(205,214,244,0.95)")
                g.addColorStop(0.35, "rgba(203,166,247,0.5)")
                g.addColorStop(1.0, "rgba(30,30,46,0.0)")
                ctx.fillStyle = g
                ctx.fillRect(0, 0, width, height)
            }
            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { from: 0.3; to: 0.85; duration: 1800; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0.3; duration: 1800; easing.type: Easing.InOutSine }
            }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 412 * root.sy
        text: "S Y N A P S E O S"
        color: root.chrome
        font.family: "Inter"
        font.pixelSize: 22 * root.sx
        font.letterSpacing: 10 * root.sx
        NumberAnimation on opacity { from: 0; to: 0.9; duration: 1300; easing.type: Easing.OutCubic }
    }

    // Slow stardust drifting upward
    Repeater {
        model: 34
        delegate: Rectangle {
            id: mote
            required property int index
            readonly property real seed: Math.abs(Math.sin(index * 12.9898) * 43758.5453) % 1
            readonly property real seed2: Math.abs(Math.sin(index * 78.233) * 12345.678) % 1
            width: (1.4 + seed2 * 1.8) * root.sx
            height: width
            radius: width / 2
            color: root.chrome
            x: seed * root.width
            opacity: 0
            SequentialAnimation {
                running: true
                loops: Animation.Infinite
                PauseAnimation { duration: 600 + mote.seed2 * 6000 }
                ParallelAnimation {
                    NumberAnimation {
                        target: mote; property: "y"
                        from: root.height * (0.55 + mote.seed * 0.45); to: root.height * (0.05 + mote.seed2 * 0.3)
                        duration: 14000 + mote.seed * 9000
                    }
                    SequentialAnimation {
                        NumberAnimation { target: mote; property: "opacity"; to: 0.15 + mote.seed2 * 0.35; duration: 2500 }
                        PauseAnimation { duration: 9000 + mote.seed * 4000 }
                        NumberAnimation { target: mote; property: "opacity"; to: 0; duration: 2500 }
                    }
                }
            }
        }
    }

    // ---------------------------------------------------------------- login panel
    Item {
        id: panel
        width: 440 * root.sx
        height: 290 * root.sy
        x: (root.width - width) / 2
        y: config.intValue("panelTop") * root.sy + slide
        opacity: 0
        property real slide: 18 * root.sy
        property real shakeX: 0
        transform: Translate { x: panel.shakeX }

        ParallelAnimation {
            id: intro
            NumberAnimation { target: panel; property: "opacity"; to: 1; duration: 750; easing.type: Easing.OutCubic }
            NumberAnimation { target: panel; property: "slide"; to: 0; duration: 750; easing.type: Easing.OutCubic }
        }
        Timer { interval: 150; running: true; onTriggered: { intro.start(); password.forceActiveFocus() } }

        SequentialAnimation {
            id: shake
            loops: 1
            NumberAnimation { target: panel; property: "shakeX"; to: -14; duration: 50 }
            NumberAnimation { target: panel; property: "shakeX"; to: 12; duration: 70 }
            NumberAnimation { target: panel; property: "shakeX"; to: -8; duration: 70 }
            NumberAnimation { target: panel; property: "shakeX"; to: 4; duration: 60 }
            NumberAnimation { target: panel; property: "shakeX"; to: 0; duration: 50 }
        }

        Column {
            anchors.fill: parent
            spacing: 12 * root.sy

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 12 * root.sx
                Rectangle {
                    width: 34 * root.sx; height: width; radius: width / 2
                    color: root.baseBg
                    border.color: root.accent; border.width: 1
                    Text {
                        anchors.centerIn: parent
                        text: root.userName.charAt(0).toUpperCase()
                        color: root.chrome
                        font.family: "Inter"; font.pixelSize: 16 * root.sx; font.weight: Font.DemiBold
                    }
                }
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.userName.toUpperCase()
                    color: root.chrome
                    font.family: "Inter"; font.pixelSize: 18 * root.sx; font.letterSpacing: 5 * root.sx
                }
            }

            TextField {
                id: password
                width: parent.width
                height: 50 * root.sy
                echoMode: TextInput.Password
                passwordCharacter: "●"
                placeholderText: "PASSWORD (PRESS ENTER FOR LIVE SESSION)"
                placeholderTextColor: "#6c7086"
                color: root.chrome
                enabled: !root.busy
                focus: true
                horizontalAlignment: TextInput.AlignHCenter
                font.family: "Inter"; font.pixelSize: 17 * root.sx; font.letterSpacing: 3 * root.sx
                selectByMouse: false
                background: Rectangle {
                    color: "#d811111b"
                    radius: 3
                    border.width: password.activeFocus ? 1.5 : 1
                    border.color: password.activeFocus ? root.accent : "#45475a"
                    Behavior on border.color { ColorAnimation { duration: 200 } }
                }
                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_F2) {
                        root.toggleSession()
                        event.accepted = true
                    }
                }
                onAccepted: root.doLogin()
                onTextEdited: if (!root.busy) status.show(keyboard.capsLock ? "CAPS LOCK IS ON" : "", root.dim)
            }

            Button {
                id: loginButton
                width: parent.width
                height: 46 * root.sy
                enabled: !root.busy
                onClicked: root.doLogin()
                contentItem: Text {
                    text: "L O G I N"
                    color: root.crustBg
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.family: "Inter"; font.pixelSize: 15 * root.sx; font.weight: Font.DemiBold
                }
                background: Rectangle {
                    radius: 3
                    opacity: loginButton.enabled ? 1 : 0.5
                    gradient: Gradient {
                        GradientStop { position: 0; color: loginButton.down ? "#b4befe" : (loginButton.hovered ? "#f5e0dc" : "#cba6f7") }
                        GradientStop { position: 1; color: loginButton.down ? "#94e2d5" : (loginButton.hovered ? "#cba6f7" : "#b4befe") }
                    }
                    border.color: "#cdd6f4"; border.width: 1
                }
            }

            // Session selector pill (F2 or click to toggle between XFCE X11 and Sway Wayland)
            Rectangle {
                id: sessionPill
                anchors.horizontalCenter: parent.horizontalCenter
                width: 290 * root.sx
                height: 28 * root.sy
                radius: 14 * root.sy
                color: sessionHover.hovered ? "#313244" : "#1e1e2e"
                border.color: sessionHover.hovered ? "#cba6f7" : "#45475a"
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: root.selectedSession === "xfce.desktop"
                        ? "SESSION: XFCE 4.20 (X11)  [F2]"
                        : "SESSION: SWAY (WAYLAND)  [F2]"
                    color: "#cdd6f4"
                    font.family: "JetBrainsMono Nerd Font"; font.pixelSize: 11 * root.sx; font.letterSpacing: 1.5 * root.sx
                }
                HoverHandler { id: sessionHover; cursorShape: Qt.PointingHandCursor }
                TapHandler { onTapped: root.toggleSession() }
            }

            Text {
                id: status
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: keyboard.capsLock ? "CAPS LOCK IS ON" : "PRESS ENTER OR CLICK LOGIN TO CONTINUE"
                color: root.dim
                font.family: "JetBrainsMono Nerd Font"; font.pixelSize: 12 * root.sx; font.letterSpacing: 2 * root.sx
                function show(msg, col) { if (msg !== "") text = msg; color = col }
            }
        }
    }

    // ---------------------------------------------------------------- power
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1000 * root.sy
        spacing: 48 * root.sx
        opacity: panel.opacity * 0.85
        Repeater {
            model: [
                { label: "SESSION [F2]", can: true, act: function() { root.toggleSession() } },
                { label: "RESTART", can: sddm.canReboot, act: function() { sddm.reboot() } },
                { label: "SHUT DOWN", can: sddm.canPowerOff, act: function() { sddm.powerOff() } }
            ]
            delegate: Text {
                required property var modelData
                visible: modelData.can
                text: modelData.label
                color: hover.hovered ? root.chrome : root.dim
                font.family: "JetBrainsMono Nerd Font"; font.pixelSize: 12 * root.sx; font.letterSpacing: 3 * root.sx
                HoverHandler { id: hover; cursorShape: Qt.PointingHandCursor }
                TapHandler { onTapped: modelData.act() }
            }
        }
    }

    // Seamless outro on login success: fade out login panel without black flash
    ParallelAnimation {
        id: outro
        running: false
        NumberAnimation { target: panel; property: "opacity"; to: 0; duration: 320; easing.type: Easing.OutQuad }
        NumberAnimation { target: panel; property: "slide"; to: 20 * root.sy; duration: 320; easing.type: Easing.InQuad }
    }
}
