const express = require('express')
const app = express()
const server = require('http').createServer(app)
const path = require('path')
const port = 3000

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../www/index.html'))
})

server.listen(port, () => console.log(`REST is listening on port ${port}!`))
