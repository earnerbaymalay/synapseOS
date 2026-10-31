/* SPDX-FileCopyrightText: 2026 SynapseOS Project
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * SynapseOS Calamares Slideshow (slideshowAPI: 2)
 * Catppuccin Mocha Mauve (#cba6f7) + Obsidian Crust (#11111b) Dark Glass
 */

import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
    width: 760
    height: 520

    // Calamares API 2 Slideshow Timing Configuration
    property int slideDuration: 7500
    property bool isPaused: false

    // Slideshow Auto-Advance Timer
    Timer {
        id: advanceTimer
        interval: presentation.slideDuration
        running: presentation.activatedInCalamares && !presentation.isPaused
        repeat: true
        onTriggered: {
            presentation.goToNextSlide();
            progressTimerAnim.restart();
        }
    }

    // Top Progress Line Animation
    NumberAnimation {
        id: progressTimerAnim
        target: navProgressBar
        property: "width"
        from: 0
        to: presentation.width
        duration: presentation.slideDuration
        running: presentation.activatedInCalamares && !presentation.isPaused
        loops: Animation.Infinite
    }

    // Calamares API 2 Lifecycle Methods
    function onActivate() {
        console.log("SynapseOS Slideshow: onActivate() triggered");
        presentation.currentSlide = 0;
        presentation.isPaused = false;
        advanceTimer.restart();
        progressTimerAnim.restart();
    }

    function onLeave() {
        console.log("SynapseOS Slideshow: onLeave() triggered");
        advanceTimer.stop();
        progressTimerAnim.stop();
    }

    // Deep Obsidian Crust Base Canvas
    Rectangle {
        id: baseCanvas
        anchors.fill: parent
        color: "#11111b"
        z: -10

        // Subtle gradient overlay for dark glass depth
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#181825" }
                GradientStop { position: 0.5; color: "#11111b" }
                GradientStop { position: 1.0; color: "#0d0d15" }
            }
        }
    }

    // ==========================================
    // TOP HEADER STRIP
    // ==========================================
    Rectangle {
        id: headerStrip
        x: 0
        y: 0
        width: parent.width
        height: 56
        color: "#181825"
        z: 20

        // Bottom border line
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: "#313244"
        }

        // Header Content Row
        Row {
            anchors.left: parent.left
            anchors.leftMargin: 24
            anchors.verticalCenter: parent.verticalCenter
            spacing: 14

            // Glowing Twin Hook Monogram Badge
            Rectangle {
                width: 32
                height: 32
                radius: 8
                color: "#11111b"
                border.color: "#cba6f7"
                border.width: 1.2
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    anchors.centerIn: parent
                    text: "S"
                    font.family: "DejaVu Sans Mono, monospace"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#cba6f7"
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2

                Row {
                    spacing: 6
                    Text {
                        text: "SYNAPSE"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#cdd6f4"
                    }
                    Text {
                        text: "OS"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#cba6f7"
                    }
                }

                Text {
                    text: "SYSTEM INSTALLATION CONTROL PLANE"
                    font.family: "DejaVu Sans Mono, monospace"
                    font.pixelSize: 9
                    font.bold: true
                    color: "#6c7086"
                }
            }
        }

        // Top Right Live Deployment Status Indicator
        Row {
            anchors.right: parent.right
            anchors.rightMargin: 24
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12

            // Pulsing Status Dot
            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#a6e3a1"
                anchors.verticalCenter: parent.verticalCenter

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 0.3; duration: 900; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 0.3; to: 1.0; duration: 900; easing.type: Easing.InOutQuad }
                }
            }

            Text {
                text: "DEPLOYING SYSTEM"
                font.family: "DejaVu Sans Mono, monospace"
                font.pixelSize: 10
                font.bold: true
                color: "#a6adc8"
                anchors.verticalCenter: parent.verticalCenter
            }

            Rectangle {
                width: 1
                height: 16
                color: "#45475a"
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: (presentation.currentSlide + 1) + " / 4"
                font.family: "DejaVu Sans Mono, monospace"
                font.pixelSize: 11
                font.bold: true
                color: "#cba6f7"
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // ==========================================
    // SLIDE 1: WELCOME TO SYNAPSEOS
    // ==========================================
    Slide {
        id: slide1
        x: 0
        y: 56
        width: parent.width
        height: parent.height - 110

        // Card Container
        Rectangle {
            anchors.fill: parent
            anchors.margins: 20
            color: "#181825"
            radius: 14
            border.color: "#313244"
            border.width: 1

            // Inner subtle rim highlight
            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                color: "transparent"
                radius: 13
                border.color: "#cba6f7"
                border.width: 1
                opacity: 0.15
            }

            Column {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                // Slide Badge Tag
                Rectangle {
                    width: badgeText1.implicitWidth + 20
                    height: 24
                    radius: 6
                    color: "#1e1e2e"
                    border.color: "#cba6f7"
                    border.width: 1

                    Text {
                        id: badgeText1
                        anchors.centerIn: parent
                        text: "CORE ARCHITECTURE · x86-64-v3"
                        font.family: "DejaVu Sans Mono, monospace"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#cba6f7"
                    }
                }

                // Slide Main Header
                Column {
                    spacing: 4
                    Text {
                        text: "Welcome to SynapseOS"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#cdd6f4"
                    }
                    Text {
                        text: "Featherlight Arch Linux Base with CachyOS BORE Response-Enhanced Kernel"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 13
                        color: "#a6adc8"
                    }
                }

                // 2x2 Feature Highlights Grid
                Grid {
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 12
                    width: parent.width

                    // Feature 1
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "CachyOS BORE Scheduler"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#cba6f7"
                            }
                            Text {
                                text: "Burst-Oriented Response Enhancer prevents interface lag and guarantees zero-jitter audio DSP."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 2
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "x86-64-v3 Instruction Set"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#89b4fa"
                            }
                            Text {
                                text: "Compiled targeting AVX2, FMA, and BMI2 vector instructions for peak computational throughput."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 3
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Sub-500MB Idle Footprint"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#a6e3a1"
                            }
                            Text {
                                text: "Zero telemetry bloat, strictly vetted background daemons, and instant cold-boot launch times."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 4
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Btrfs Snapshots & Recovery"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#f9e2af"
                            }
                            Text {
                                text: "Engineered subvolume layout (@, @home, @snapshots, @var_log) with instant rollback capabilities."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SLIDE 2: LOCAL AI & SYNAPSE MEMORY ENGINE
    // ==========================================
    Slide {
        id: slide2
        x: 0
        y: 56
        width: parent.width
        height: parent.height - 110

        Rectangle {
            anchors.fill: parent
            anchors.margins: 20
            color: "#181825"
            radius: 14
            border.color: "#313244"
            border.width: 1

            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                color: "transparent"
                radius: 13
                border.color: "#cba6f7"
                border.width: 1
                opacity: 0.15
            }

            Column {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                Rectangle {
                    width: badgeText2.implicitWidth + 20
                    height: 24
                    radius: 6
                    color: "#1e1e2e"
                    border.color: "#cba6f7"
                    border.width: 1

                    Text {
                        id: badgeText2
                        anchors.centerIn: parent
                        text: "SOVEREIGN MACHINE INTELLIGENCE · PORT 11434"
                        font.family: "DejaVu Sans Mono, monospace"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#cba6f7"
                    }
                }

                Column {
                    spacing: 4
                    Text {
                        text: "Local AI & Synapse Memory Engine"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#cdd6f4"
                    }
                    Text {
                        text: "Zero-Cloud LLM Execution with Persistent Knowledge & HUD Overlay"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 13
                        color: "#a6adc8"
                    }
                }

                Grid {
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 12
                    width: parent.width

                    // Feature 1
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Resident Ollama AI Daemon"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#cba6f7"
                            }
                            Text {
                                text: "Configured locally at port 11434 with single-threaded CPU protection and 24h keep-alive."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 2
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Quickfire HUD (Super+Space)"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#89b4fa"
                            }
                            Text {
                                text: "Instantaneous heads-up terminal overlay for code generation, piping, and desktop queries."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 3
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Synapse Memory Engine"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#a6e3a1"
                            }
                            Text {
                                text: "Cross-session semantic recall and knowledge graph persistence stored strictly on local NVMe."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 4
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "CPU Concurrency Throttling"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#f9e2af"
                            }
                            Text {
                                text: "Ananicy-cpp process scheduling prioritizing desktop interactive frames over heavy model weights."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SLIDE 3: PRIME DIRECTIVE STEALTH & ANONYMITY
    // ==========================================
    Slide {
        id: slide3
        x: 0
        y: 56
        width: parent.width
        height: parent.height - 110

        Rectangle {
            anchors.fill: parent
            anchors.margins: 20
            color: "#181825"
            radius: 14
            border.color: "#313244"
            border.width: 1

            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                color: "transparent"
                radius: 13
                border.color: "#cba6f7"
                border.width: 1
                opacity: 0.15
            }

            Column {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                Rectangle {
                    width: badgeText3.implicitWidth + 20
                    height: 24
                    radius: 6
                    color: "#1e1e2e"
                    border.color: "#cba6f7"
                    border.width: 1

                    Text {
                        id: badgeText3
                        anchors.centerIn: parent
                        text: "PRIME DIRECTIVE · SECURITY & ANONYMITY FIRST"
                        font.family: "DejaVu Sans Mono, monospace"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#cba6f7"
                    }
                }

                Column {
                    spacing: 4
                    Text {
                        text: "Prime Directive Stealth & Anonymity"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#cdd6f4"
                    }
                    Text {
                        text: "Counter-Surveillance Networking & Hardware Identity Obfuscation"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 13
                        color: "#a6adc8"
                    }
                }

                Grid {
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 12
                    width: parent.width

                    // Feature 1
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Dual MAC Randomization"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#cba6f7"
                            }
                            Text {
                                text: "Hardware MAC is strictly masked; random identifiers generated per scan and per connection session."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 2
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "DNS-over-TLS (DoT Port 853)"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#89b4fa"
                            }
                            Text {
                                text: "Encrypted Quad9 resolver (9.9.9.9) via systemd-resolved preventing ISP snooping and DNS poisoning."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 3
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Stealth Firewall Posture"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#a6e3a1"
                            }
                            Text {
                                text: "Default DROP inbound policy, ICMP ping echo-requests ignored, mDNS and Avahi broadcasts silenced."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 4
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "RFC 4941 IPv6 Privacy"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#f9e2af"
                            }
                            Text {
                                text: "Temporary randomized IPv6 interface addresses enforced for all outgoing Internet traffic."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SLIDE 4: CYBERDECK DESKTOP
    // ==========================================
    Slide {
        id: slide4
        x: 0
        y: 56
        width: parent.width
        height: parent.height - 110

        Rectangle {
            anchors.fill: parent
            anchors.margins: 20
            color: "#181825"
            radius: 14
            border.color: "#313244"
            border.width: 1

            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                color: "transparent"
                radius: 13
                border.color: "#cba6f7"
                border.width: 1
                opacity: 0.15
            }

            Column {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                Rectangle {
                    width: badgeText4.implicitWidth + 20
                    height: 24
                    radius: 6
                    color: "#1e1e2e"
                    border.color: "#cba6f7"
                    border.width: 1

                    Text {
                        id: badgeText4
                        anchors.centerIn: parent
                        text: "CYBERDECK INTERFACE · CATPPUCCIN MOCHA"
                        font.family: "DejaVu Sans Mono, monospace"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#cba6f7"
                    }
                }

                Column {
                    spacing: 4
                    Text {
                        text: "Cyberdeck Desktop Experience"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#cdd6f4"
                    }
                    Text {
                        text: "Dark Glass Aesthetics, Dual Kawase Blur & Liquid Silver Chrome"
                        font.family: "DejaVu Sans, Inter, sans-serif"
                        font.pixelSize: 13
                        color: "#a6adc8"
                    }
                }

                Grid {
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 12
                    width: parent.width

                    // Feature 1
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Catppuccin Mocha Mauve"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#cba6f7"
                            }
                            Text {
                                text: "Cohesive aesthetic (#cba6f7 / #11111b) tuned across XFCE 4.20, Sway, Kitty, and Waybar."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 2
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Liquid Chrome Vector Icons"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#89b4fa"
                            }
                            Text {
                                text: "Machined metal chamfers, 45-degree specular reflection wireframes, and horizon gloss."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 3
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Dual Kawase Translucency"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#a6e3a1"
                            }
                            Text {
                                text: "Hardware-accelerated window compositor with GPU dual-kawase blur and smooth corner radii."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }

                    // Feature 4
                    Rectangle {
                        width: (parent.width - 16) / 2
                        height: 72
                        color: "#1e1e2e"
                        radius: 8
                        border.color: "#313244"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 3
                            Text {
                                text: "Chromatic Theme Switcher"
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 12
                                font.bold: true
                                color: "#f9e2af"
                            }
                            Text {
                                text: "Press Super+Ctrl+T to hot-swap between Mauve, Sapphire, Emerald, Crimson, and Tungsten."
                                font.family: "DejaVu Sans, Inter, sans-serif"
                                font.pixelSize: 11
                                color: "#a6adc8"
                                wrapMode: Text.WordWrap
                                width: parent.width
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // BOTTOM NAVIGATION STRIP
    // ==========================================
    Rectangle {
        id: bottomStrip
        x: 0
        y: parent.height - 54
        width: parent.width
        height: 54
        color: "#181825"
        z: 20

        // Top border line
        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: "#313244"
        }

        // Animated Slide Auto-Advance Progress Bar
        Rectangle {
            id: navProgressBar
            x: 0
            y: 0
            height: 2
            color: "#cba6f7"
        }

        // Navigation Controls Container
        Item {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 24

            // Left: Previous Slide Button
            Rectangle {
                width: 32
                height: 32
                radius: 8
                color: prevArea.containsMouse ? "#313244" : "#1e1e2e"
                border.color: prevArea.containsMouse ? "#cba6f7" : "#45475a"
                border.width: 1
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    anchors.centerIn: parent
                    text: "<"
                    font.family: "DejaVu Sans Mono, monospace"
                    font.pixelSize: 15
                    font.bold: true
                    color: prevArea.containsMouse ? "#cba6f7" : "#cdd6f4"
                }

                MouseArea {
                    id: prevArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        presentation.goToPrevSlide();
                        progressTimerAnim.restart();
                    }
                }
            }

            // Center: Interactive Slide Indicator Pills
            Row {
                anchors.centerIn: parent
                spacing: 10

                Repeater {
                    model: 4

                    Rectangle {
                        id: dot
                        width: (presentation.currentSlide === index) ? 28 : 10
                        height: 10
                        radius: 5
                        color: (presentation.currentSlide === index) ? "#cba6f7" : (dotArea.containsMouse ? "#6c7086" : "#313244")

                        Behavior on width {
                            NumberAnimation { duration: 250; easing.type: Easing.OutQuad }
                        }
                        Behavior on color {
                            ColorAnimation { duration: 200 }
                        }

                        MouseArea {
                            id: dotArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                presentation.currentSlide = index;
                                progressTimerAnim.restart();
                            }
                        }
                    }
                }
            }

            // Right: Next Slide Button
            Rectangle {
                width: 32
                height: 32
                radius: 8
                color: nextArea.containsMouse ? "#313244" : "#1e1e2e"
                border.color: nextArea.containsMouse ? "#cba6f7" : "#45475a"
                border.width: 1
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    anchors.centerIn: parent
                    text: ">"
                    font.family: "DejaVu Sans Mono, monospace"
                    font.pixelSize: 15
                    font.bold: true
                    color: nextArea.containsMouse ? "#cba6f7" : "#cdd6f4"
                }

                MouseArea {
                    id: nextArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        presentation.goToNextSlide();
                        progressTimerAnim.restart();
                    }
                }
            }
        }
    }
}
