import QtQuick 2.15
Item {
    id: root
    property var slides: []
    property int currentSlide: 0
    property bool loopSlides: true
    property bool activatedInCalamares: true
    default property alias children: root.data

    Component.onCompleted: {
        var s = [];
        for (var i = 0; i < root.children.length; ++i) {
            var c = root.children[i];
            if (c.isSlide) {
                s.push(c);
                c.visible = (s.length === 1);
            }
        }
        root.slides = s;
    }

    onCurrentSlideChanged: {
        for (var i = 0; i < slides.length; ++i) {
            slides[i].visible = (i === currentSlide);
        }
    }

    function goToNextSlide() {
        if (slides.length > 0) {
            currentSlide = (currentSlide + 1) % slides.length;
        }
    }

    function goToPrevSlide() {
        if (slides.length > 0) {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        }
    }
}
