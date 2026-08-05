import { useEffect, useState } from "react";

export function useCountdown(initialSeconds = 0) {
  const [secondsRemaining, setSecondsRemaining] = useState(initialSeconds);

  useEffect(() => {
    if (secondsRemaining <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setSecondsRemaining((current) => Math.max(0, current - 1));
    }, 1_000);

    return () => window.clearInterval(timer);
  }, [secondsRemaining]);

  return {
    secondsRemaining,
    start: setSecondsRemaining,
  };
}
