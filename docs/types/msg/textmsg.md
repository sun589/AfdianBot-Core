# 文本消息类型(TextMsg)

## TextMsg

| 字段名       | 类型     | 描述                 |
| --------- | ------ | ------------------ |
| msg_type  | string | 消息类型(send/receive) |
| msg_id    | int    | 消息 ID              |
| id        | int    | 同send_time         |
| content   | string | 消息内容               |
| sender_id | int    | 发送者id              |
| send_time | int    | 消息发送的时间戳           |
