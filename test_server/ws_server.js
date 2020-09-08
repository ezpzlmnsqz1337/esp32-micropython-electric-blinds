const WebSocket = require("ws");

const wss = new WebSocket.Server({ port: 8085 });
console.log("Server is listenning on port: 8085");

blinds = [0, 0];

wss.on("connection", (ws) => {
  // send initial configuration

  ws.on("message", (message) => {
    console.log("message: ", message);
    if (message.includes("up")) {
      const blindIndex = parseInt(message.substring(message.indexOf(":") + 1));
      const steps = parseInt(message.substring(message.lastIndexOf(":") + 1));
      blinds[blindIndex] += steps;
      wss.clients.forEach((client) => {
        client.send("blindsPosition:" + blinds.join("|"));
      });
    } else if (message.includes("down")) {
      const blindIndex = parseInt(message.substring(message.indexOf(":") + 1));
      const steps = parseInt(message.substring(message.lastIndexOf(":") + 1));
      blinds[blindIndex] -= steps;
      wss.clients.forEach((client) => {
        client.send("blindsPosition:" + blinds.join("|"));
      });
    } else if (message.includes("stop")) {
      const blindIndex = parseInt(message.substring(message.indexOf(":") + 1));
      wss.clients.forEach((client) => {
        client.send("stopping:" + blindIndex);
      });
    } else if (message.includes("open")) {
      const blindIndex = parseInt(message.substring(message.indexOf(":") + 1));
      wss.clients.forEach((client) => {
        client.send("opening:" + blindIndex);
      });
    } else if (message.includes("close")) {
      blindIndex = parseInt(message.substring(message.indexOf(":") + 1));
      wss.clients.forEach((client) => {
        client.send("closing:" + blindIndex);
      });
    }
  });

  // setInterval(() => ws.send('blinds:90|150|160|30|closed'), 2000)
});
