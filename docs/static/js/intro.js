(() => {
  "use strict";

  const trigger = document.querySelector(".auth-trigger");
  const panel = document.querySelector(".gateway-panel");
  const fill = document.querySelector("[data-progress-fill]");
  const securityCode = document.querySelector("[data-security-code]");

  if (!trigger || !panel || !fill || !securityCode) {
    return;
  }

  const finalCode = "SECURITY ACCESS VERIFIED";
  const scrambleChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@$%&";
  const totalDuration = 2800;
  let isAuthenticating = false;

  const randomChar = () => scrambleChars[Math.floor(Math.random() * scrambleChars.length)];

  const setProgress = (percent) => {
    const rounded = Math.round(percent);
    fill.style.width = `${rounded}%`;
  };

  const setSecurityCode = (percent) => {
    let nextCode = "";

    for (let index = 0; index < finalCode.length; index += 1) {
      const targetChar = finalCode[index];

      if (targetChar === " ") {
        nextCode += targetChar;
        continue;
      }

      nextCode += randomChar();
    }

    securityCode.textContent = percent >= 100 ? finalCode : nextCode;
  };

  const finishAuthentication = () => {
    setProgress(100);
    setSecurityCode(100);
    panel.classList.add("is-unlocked");

    window.setTimeout(() => {
      document.body.classList.add("is-exiting");
      window.setTimeout(() => {
        window.location.href = trigger.href;
      }, 500);
    }, 500);
  };

  const animateProgress = (startTime) => {
    const elapsed = performance.now() - startTime;
    const progress = Math.min(elapsed / totalDuration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const percent = eased * 100;

    setProgress(percent);
    setSecurityCode(percent);

    if (progress < 1) {
      window.requestAnimationFrame(() => animateProgress(startTime));
      return;
    }

    finishAuthentication();
  };

  trigger.addEventListener("click", (event) => {
    event.preventDefault();

    if (isAuthenticating) {
      return;
    }

    isAuthenticating = true;
    panel.classList.add("is-authenticating");
    trigger.setAttribute("aria-disabled", "true");
    setProgress(0);
    setSecurityCode(0);

    window.requestAnimationFrame((timestamp) => {
      animateProgress(timestamp);
    });
  });
})();
