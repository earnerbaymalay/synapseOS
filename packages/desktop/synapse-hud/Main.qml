// SynapseOS — Command HUD & Quickfire Cockpit (Qt6 / Material You)
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Shapes
import QtQuick.Effects

Window {
    id: root
    width: 960
    height: 640
    visible: true
    title: "Synapse Command HUD"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog
    color: "transparent"

    readonly property var accents: ({
        mauve: "#cba6f7", tungsten: "#fab387", crimson: "#f38ba8",
        sapphire: "#74c7ec", emerald: "#a6e3a1"
    })
    property string variant: "monolith-mauve"
    readonly property color accent: accents[variant.split("-").pop()] || accents.mauve
    readonly property color surface: "#181825"
    readonly property color surfaceContainer: "#1e1e2e"
    readonly property color textMain: "#cdd6f4"
    readonly property color textSub: "#a6adc8"
    readonly property color borderMuted: "#313244"
    readonly property string mono: "JetBrainsMono Nerd Font"

    signal launchCommand(string action)
    signal closeHud()

    Component.onCompleted: {
        searchBox.forceActiveFocus()
    }

    FocusScope {
        id: panel
        anchors.fill: parent
        anchors.margins: 12
        focus: true
        readonly property real c: 18

        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Escape) {
                root.closeHud()
                event.accepted = true
                return
            }
            if (searchBox.text.length === 0) {
                var k = event.text.toUpperCase()
                var action = findCommandByKey(k)
                if (action !== "") {
                    root.launchCommand(action)
                    event.accepted = true
                }
            }
        }

        // Drop shadow / glow border
        Rectangle {
            anchors.fill: parent
            anchors.margins: -4
            color: "transparent"
            border.color: root.accent
            border.width: 1
            opacity: 0.35
            radius: panel.c + 2
        }

        // Chamfered Background Body
        Shape {
            anchors.fill: parent
            preferredRendererType: Shape.CurveRenderer
            ShapePath {
                strokeWidth: 1.5
                strokeColor: root.borderMuted
                fillColor: Qt.rgba(13 / 255, 14 / 255, 21 / 255, 0.95)
                startX: panel.c; startY: 0
                PathLine { x: panel.width - panel.c; y: 0 }
                PathLine { x: panel.width; y: panel.c }
                PathLine { x: panel.width; y: panel.height - panel.c }
                PathLine { x: panel.width - panel.c; y: panel.height }
                PathLine { x: panel.c; y: panel.height }
                PathLine { x: 0; y: panel.height - panel.c }
                PathLine { x: 0; y: panel.c }
                PathLine { x: panel.c; y: 0 }
            }
        }

        // Animated travelling border trails
        Shape {
            id: trails
            anchors.fill: parent
            readonly property real perim: 2 * (panel.width + panel.height)
            property real offset: 0
            NumberAnimation on offset {
                loops: Animation.Infinite
                from: trails.perim; to: 0
                duration: 6500
            }
            ShapePath {
                strokeColor: root.accent
                strokeWidth: 2
                fillColor: "transparent"
                strokeStyle: ShapePath.DashLine
                dashPattern: [12, 120]
                dashOffset: trails.offset
                startX: panel.c; startY: 0
                PathLine { x: panel.width - panel.c; y: 0 }
                PathLine { x: panel.width; y: panel.c }
                PathLine { x: panel.width; y: panel.height - panel.c }
                PathLine { x: panel.width - panel.c; y: panel.height }
                PathLine { x: panel.c; y: panel.height }
                PathLine { x: 0; y: panel.height - panel.c }
                PathLine { x: 0; y: panel.c }
                PathLine { x: panel.c; y: 0 }
            }
        }

        // --- Content Column ---
        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header Row
            Item {
                width: parent.width
                height: 24

                Text {
                    id: headerTitle
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: "󰚩 SYNAPSE COMMAND HUD"
                    color: root.accent
                    font { family: root.mono; pixelSize: 13; bold: true; letterSpacing: 1.2 }
                }

                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 12

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "[Esc] Close · [Enter] Launch / Ask AI · [Ctrl+Enter] Ask AI"
                        color: "#6c7086"
                        font { family: root.mono; pixelSize: 11 }
                    }

                    Rectangle {
                        id: closeBtn
                        width: 24
                        height: 24
                        radius: 6
                        color: closeMouseArea.containsMouse ? "#f38ba8" : "#313244"
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            color: closeMouseArea.containsMouse ? "#11111b" : "#cdd6f4"
                            font { family: root.mono; pixelSize: 12; bold: true }
                        }

                        MouseArea {
                            id: closeMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.closeHud()
                        }
                    }
                }
            }

            // Search Bar Input
            Rectangle {
                width: parent.width
                height: 44
                radius: 12
                color: root.surface
                border.color: searchBox.activeFocus ? root.accent : root.borderMuted
                border.width: 1

                Row {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    Text {
                        text: "󰍉"
                        color: searchBox.activeFocus ? root.accent : root.textSub
                        font { family: root.mono; pixelSize: 16 }
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    TextInput {
                        id: searchBox
                        width: parent.width - 40
                        anchors.verticalCenter: parent.verticalCenter
                        color: root.textMain
                        font { family: root.mono; pixelSize: 13 }
                        selectByMouse: true
                        selectionColor: root.accent
                        selectedTextColor: "#11111b"

                        Text {
                            text: "[Esc] Close · [Enter] Launch / Ask AI · [Ctrl+Enter] Ask AI"
                            color: "#6c7086"
                            font: searchBox.font
                            visible: !searchBox.text && !searchBox.activeFocus
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Keys.onPressed: function(event) {
                            if (event.key === Qt.Key_Escape) {
                                root.closeHud()
                                event.accepted = true
                                return
                            }
                            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                var q = searchBox.text.trim()
                                if (q.length > 0) {
                                    var isCtrl = (event.modifiers & Qt.ControlModifier) !== 0
                                    var isAiExplicit = q.startsWith("?") || q.toLowerCase().startsWith("ai ")
                                    if (isCtrl || isAiExplicit) {
                                        root.launchCommand("AI_PROMPT:" + q)
                                    } else {
                                        var match = root.findFirstMatch(q)
                                        if (match !== "") {
                                            root.launchCommand(match)
                                        } else {
                                            root.launchCommand("AI_PROMPT:" + q)
                                        }
                                    }
                                    event.accepted = true
                                }
                                return
                            }
                            if (searchBox.text.length === 0) {
                                var k = event.text.toUpperCase()
                                var action = findCommandByKey(k)
                                if (action !== "") {
                                    root.launchCommand(action)
                                    event.accepted = true
                                }
                            }
                        }
                    }
                }
            }

            // Grid of 6 Categorized Command Cards
            Grid {
                id: commandGrid
                width: parent.width
                columns: 3
                spacing: 12

                // Section 1: AI Agents & Brain
                CommandCategoryCard {
                    title: "🧠 AI AGENTS & BRAIN"
                    accentColor: root.accent
                    items: [
                        { key: "1", label: "synapse hud", desc: "Cockpit TUI", cmd: "kitty --title 'Synapse HUD' synapse hud" },
                        { key: "2", label: "synapse sync", desc: "Sync Brain", cmd: "kitty --hold synapse sync --once" },
                        { key: "3", label: "synapse vibe", desc: "Line Stats", cmd: "kitty --hold synapse vibe --hours 24" },
                        { key: "4", label: "agy", desc: "Interactive CLI", cmd: "kitty agy" },
                        { key: "5", label: "claude", desc: "Agent CLI", cmd: "kitty claude" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }

                // Section 2: Local LLMs
                CommandCategoryCard {
                    title: "⚡ LOCAL INFERENCE"
                    accentColor: "#fab387"
                    items: [
                        { key: "Q", label: "ask-qwen", desc: "Qwen 2.5 Coder", cmd: "kitty bash -c 'read -p \"Ask Qwen: \" q; [[ -n \"$q\" ]] && ask-qwen \"$q\"; echo; read -p \"Press enter to close...\"'" },
                        { key: "L", label: "ask-llama", desc: "LLaMA 3.2", cmd: "kitty bash -c 'read -p \"Ask LLaMA: \" q; [[ -n \"$q\" ]] && ask-llama \"$q\"; echo; read -p \"Press enter to close...\"'" },
                        { key: "W", label: "ai warm", desc: "Preload RAM", cmd: "bash -c 'ai warm && notify-send \"AI Engine\" \"Pre-warmed code model\"'" },
                        { key: "F", label: "ai flush", desc: "Free RAM", cmd: "bash -c 'ai flush && notify-send \"AI Engine\" \"Flushed resident models\"'" },
                        { key: "O", label: "oterm", desc: "Chat TUI", cmd: "kitty oterm" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }

                // Section 3: Stealth & Security
                CommandCategoryCard {
                    title: "🛡️ STEALTH & SECURITY"
                    accentColor: "#a6e3a1"
                    items: [
                        { key: "A", label: "lab audit", desc: "Prime Directive", cmd: "kitty --hold lab audit" },
                        { key: "S", label: "sec-status", desc: "MAC & DoT Check", cmd: "kitty --hold sec-status" },
                        { key: "H", label: "wifi-home", desc: "Home WPA3-SAE", cmd: "wifi-home" },
                        { key: "T", label: "wifi-hotspot", desc: "Mobile Failover", cmd: "wifi-hotspot" },
                        { key: "D", label: "firewall-drop", desc: "Drop Inbound", cmd: "kitty --hold sudo firewall-cmd --state" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }

                // Section 4: Audio & Hardware
                CommandCategoryCard {
                    title: "🔊 AUDIO & HARDWARE"
                    accentColor: "#74c7ec"
                    items: [
                        { key: "Z", label: "audio-switch", desc: "Output Picker", cmd: "audio-switch" },
                        { key: "X", label: "q1-mode", desc: "FiiO SBC-XQ", cmd: "bash -c 'q1-mode music && notify-send \"Audio\" \"Q1 set to SBC-XQ\"'" },
                        { key: "C", label: "pipewire", desc: "Restart Audio", cmd: "bash -c 'systemctl --user restart pipewire wireplumber && notify-send \"Audio\" \"Restarted services\"'" },
                        { key: "V", label: "throttled", desc: "25W PL1 Boost", cmd: "kitty --hold systemctl status throttled" },
                        { key: "M", label: "mem-search", desc: "Agent Memory", cmd: "kitty bash -c 'read -p \"Search Memory: \" q; [[ -n \"$q\" ]] && synapse mem search \"$q\"; echo; read -p \"Press enter to close...\"'" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }

                // Section 5: Lab & Pentest
                CommandCategoryCard {
                    title: "🎯 LAB & PENTEST"
                    accentColor: "#f38ba8"
                    items: [
                        { key: "P", label: "rf-scan", desc: "Passive Survey", cmd: "kitty --hold rf-lab scan" },
                        { key: "R", label: "auto-pentest", desc: "AI Audit Loop", cmd: "kitty lab pentest" },
                        { key: "G", label: "lazygit", desc: "Delta Git TUI", cmd: "kitty lazygit" },
                        { key: "Y", label: "yazi", desc: "File Manager", cmd: "kitty yazi" },
                        { key: "K", label: "squash", desc: "Token Compressor", cmd: "kitty bash -c 'read -p \"Command to squash: \" cmd; [[ -n \"$cmd\" ]] && squash $cmd; echo; read -p \"Press enter to close...\"'" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }

                // Section 6: Desktop & Settings
                CommandCategoryCard {
                    title: "🎨 APPS & SETTINGS"
                    accentColor: root.accent
                    items: [
                        { key: "N", label: "synapse-notes", desc: "Scratchpad Notes", cmd: "synapse-notes" },
                        { key: "E", label: "synapse-settings", desc: "Control Center", cmd: "synapse-settings" },
                        { key: "B", label: "chromium", desc: "Web Browser", cmd: "chromium" },
                        { key: "J", label: "galculator", desc: "Calculator", cmd: "galculator" },
                        { key: "U", label: "screensaver", desc: "Purple Donut", cmd: "synapse-screensaver --mode donut" }
                    ]
                    filterText: searchBox.text
                    onItemTriggered: function(c) { root.launchCommand(c) }
                }
            }
        }
    }

    function findFirstMatch(query) {
        if (!query) return ""
        var q = query.trim().toLowerCase()
        if (q === "") return ""
        for (var i = 0; i < commandGrid.children.length; ++i) {
            var cat = commandGrid.children[i]
            if (cat && cat.items) {
                for (var j = 0; j < cat.items.length; ++j) {
                    var item = cat.items[j]
                    if ((item.label && item.label.toLowerCase().indexOf(q) !== -1) ||
                        (item.desc && item.desc.toLowerCase().indexOf(q) !== -1) ||
                        (item.key && item.key.toLowerCase() === q) ||
                        (item.cmd && item.cmd.toLowerCase().indexOf(q) !== -1)) {
                        return item.cmd
                    }
                }
            }
        }
        return ""
    }

    function findCommandByKey(key) {
        for (var i = 0; i < commandGrid.children.length; ++i) {
            var cat = commandGrid.children[i]
            if (cat.items) {
                for (var j = 0; j < cat.items.length; ++j) {
                    if (cat.items[j].key.toUpperCase() === key) {
                        return cat.items[j].cmd
                    }
                }
            }
        }
        return ""
    }
}
