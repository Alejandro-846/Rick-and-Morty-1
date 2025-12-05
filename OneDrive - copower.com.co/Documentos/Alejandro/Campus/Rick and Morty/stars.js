(function () {
    let width,
        height,
        canvas,
        ctx,
        points,
        target,
        animateCanvas = true;

    // Main
    initCanvas();
    initAnimation();
    addListeners();

    function initCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        target = { x: width / 2, y: height / 2 };

        canvas = document.getElementById("starCanvas");
        canvas.width = width;
        canvas.height = height;
        ctx = canvas.getContext("2d");

        // crear puntos
        points = [];
        for (let x = 0; x < width; x = x + width / 20) {
            for (let y = 0; y < height; y = y + height / 20) {
                let px = x + (Math.random() * width) / 20;
                let py = y + (Math.random() * height) / 20;
                let p = { x: px, originX: px, y: py, originY: py };
                points.push(p);
            }
        }

        // para cada punto encontrar los 5 más cercanos
        for (let i = 0; i < points.length; i++) {
            let closest = [];
            let p1 = points[i];
            for (let j = 0; j < points.length; j++) {
                let p2 = points[j];
                if (!(p1 == p2)) {
                    let placed = false;
                    for (let k = 0; k < 5; k++) {
                        if (!placed) {
                            if (closest[k] == undefined) {
                                closest[k] = p2;
                                placed = true;
                            }
                        }
                    }

                    for (let k = 0; k < 5; k++) {
                        if (!placed) {
                            if (getDistance(p1, p2) < getDistance(p1, closest[k])) {
                                closest[k] = p2;
                                placed = true;
                            }
                        }
                    }
                }
            }
            p1.closest = closest;
        }

        // asignar un círculo a cada punto
        for (let i in points) {
            let c = new Circle(
                points[i],
                2 + Math.random() * 2,
                "rgba(156,217,249,0.5)"
            );
            points[i].circle = c;
        }
    }

    // Manejador de eventos
    function addListeners() {
        if (!("ontouchstart" in window)) {
            window.addEventListener("mousemove", mouseMove);
        }
        window.addEventListener("scroll", scrollCheck);
        window.addEventListener("resize", resize);
    }

    function mouseMove(e) {
        let posy = 0;
        let posx = 0;
        if (e.pageX || e.pageY) {
            posx = e.pageX;
            posy = e.pageY;
        } else if (e.clientX || e.clientY) {
            posx =
                e.clientX +
                document.body.scrollLeft +
                document.documentElement.scrollLeft;
            posy =
                e.clientY +
                document.body.scrollTop +
                document.documentElement.scrollTop;
        }
        target.x = posx;
        target.y = posy;
    }

    function scrollCheck() {
        if (document.body.scrollTop > height) animateCanvas = false;
        else animateCanvas = true;
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }

    // animación
    function initAnimation() {
        animate();
        for (let i in points) {
            shiftPoint(points[i]);
        }
    }

    function animate() {
        if (animateCanvas) {
            ctx.clearRect(0, 0, width, height);
            for (let i in points) {
                // detectar puntos en rango
                if (Math.abs(getDistance(target, points[i])) < 4000) {
                    points[i].active = 0.3;
                    points[i].circle.active = 0.6;
                } else if (Math.abs(getDistance(target, points[i])) < 20000) {
                    points[i].active = 0.1;
                    points[i].circle.active = 0.3;
                } else if (Math.abs(getDistance(target, points[i])) < 40000) {
                    points[i].active = 0.02;
                    points[i].circle.active = 0.1;
                } else {
                    points[i].active = 0;
                    points[i].circle.active = 0;
                }

                drawLines(points[i]);
                points[i].circle.draw();
            }
        }
        requestAnimationFrame(animate);
    }

    function shiftPoint(p) {
        let duration = 1 + 1 * Math.random();
        let startX = p.x;
        let startY = p.y;
        let targetX = p.originX - 50 + Math.random() * 100;
        let targetY = p.originY - 50 + Math.random() * 100;
        let startTime = null;

        function animate(timestamp) {
            if (!startTime) startTime = timestamp;
            let progress = (timestamp - startTime) / (duration * 1000);

            if (progress < 1) {
                p.x = startX + (targetX - startX) * easeInOutCirc(progress);
                p.y = startY + (targetY - startY) * easeInOutCirc(progress);
                requestAnimationFrame(animate);
            } else {
                p.x = targetX;
                p.y = targetY;
                shiftPoint(p);
            }
        }

        requestAnimationFrame(animate);
    }

    function easeInOutCirc(t) {
        return t < 0.5
            ? (1 - Math.sqrt(1 - Math.pow(2 * t, 2))) / 2
            : (Math.sqrt(1 - Math.pow(-2 * t + 2, 2)) + 1) / 2;
    }

    // Manipulación del canvas
    function drawLines(p) {
        if (!p.active) return;
        for (let i in p.closest) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.closest[i].x, p.closest[i].y);
            ctx.strokeStyle = "rgba(156,217,249," + p.active + ")";
            ctx.stroke();
        }
    }

    function Circle(pos, rad, color) {
        let _this = this;

        // constructor
        (function () {
            _this.pos = pos || null;
            _this.radius = rad || null;
            _this.color = color || null;
        })();

        this.draw = function () {
            if (!_this.active) return;
            ctx.beginPath();
            ctx.arc(_this.pos.x, _this.pos.y, _this.radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = "rgba(156,217,249," + _this.active + ")";
            ctx.fill();
        };
    }

    // Utilidades
    function getDistance(p1, p2) {
        return Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2);
    }
})();

// Estrellas parpadeantes adicionales
(function () {
    let stars = [];

    function createStars(count) {
        const starsContainer = document.getElementById('stars');
        for (let i = 0; i < count; i++) {
            drawStars(starsContainer);
        }
    }

    function drawStars(container) {
        let tmpStar = document.createElement('div');
        tmpStar.className = "star";
        tmpStar.style.top = 100 * Math.random() + '%';
        tmpStar.style.left = 100 * Math.random() + '%';
        tmpStar.style.animationDelay = Math.random() * 2 + 's';
        container.appendChild(tmpStar);
        stars.push(tmpStar);
    }

    function animateStars() {
        stars.forEach(function (el) {
            let duration = Math.random() * 0.5 + 0.5;
            let opacity = Math.random();
            el.style.transition = `opacity ${duration}s ease-in-out`;
            el.style.opacity = opacity;
        });
        setTimeout(animateStars, 1000);
    }

    // Inicializar
    createStars(500);
    animateStars();
})();
