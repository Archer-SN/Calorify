const createEnergyChart = (element, energyHistory) => {
  console.log(energyHistory[0]);
  new Chart(element, {
    type: "bar",
    data: {
      datasets: [
        {
          data: energyHistory,
          label: "Energy Consumed",
          backgroundColor: "#c084fc",
        },
      ],
    },
    options: {
      animations: {
        y: {
          duration: 1000,
          easing: "linear",
        },
      },
    },
  });
};
