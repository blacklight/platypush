import mitt from 'mitt'

const bus = mitt()

bus.publishEntity = (entity) => {
  bus.emit('entity-update', entity)
}

bus.onEntity = (callback) => {
  bus.on('entity-update', callback)
}

bus.publishNotification = (notification) => {
  bus.emit('notification-create', notification)
}

bus.onNotification = (callback) => {
  bus.on('notification-create', callback)
}

export { bus }
