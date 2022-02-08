// Some random colors
const colors = ["#FED10A", "#7DE2D1", "#EF5098", "#17A8E0", "#93C83E", "#FED10A", "#7DE2D1", "#EF5098", "#17A8E0", "#93C83E","#FED10A", "#7DE2D1", "#EF5098", "#17A8E0", "#93C83E"];

const numBalls = 15;
const balls = [];

for (let i = 0; i < numBalls; i++) {
  let ball = document.createElement("div");
  ball.classList.add("ball");
  ball.style.background = colors[i];
  ball.style.left = `${Math.floor(Math.random() * 85)}vw`;
  ball.style.top = `${Math.floor(Math.random() * 10)}vh`;
  ball.style.transform = `scale(${Math.random()})`;
  ball.style.width = `${Math.random()*20}em`;
  ball.style.height = ball.style.width;

  balls.push(ball);
  document.body.append(ball);
}

// Keyframes
balls.forEach((el, i, ra) => {
  let to = {
    x: Math.random() * (i % 2 === 0 ? -0.5 : 0.5),
    y: Math.random() * 2
  };

  let anim = el.animate(
    [
      { transform: "translate(0, 0)" },
      { transform: `translate(${to.x}rem, ${to.y}rem)` }
    ],
    {
      duration: (Math.random() + 1) * 2000, // random duration
      direction: "alternate",
      fill: "both",
      iterations: Infinity,
      easing: "ease-in-out"
    }
  );
});