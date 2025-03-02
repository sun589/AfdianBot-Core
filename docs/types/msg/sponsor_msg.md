# 赞助消息(SponsorMsg)

## SponsorMsg

| 字段名         | 类型      | 描述                 |
| ----------- | ------- | ------------------ |
| msg_type    | string  | 消息类型(send/receive) |
| msg_id      | int     | 消息 ID              |
| id          | int     | 同send_time         |
| sender_id   | int     | 发送者id              |
| send_time   | int     | 消息发送的时间戳           |
| amount      | float   | 赞助金额               |
| real_amount | float   | 实际金额(添加到账户的金额)     |
| plan_id     | string  | 方案id               |
| remark      | string  | 备注                 |
| phone       | string  | 手机号                |
| address     | string  | 收货地址               |
| recipient   | string  | 收件人                |
| isupgrade   | boolean | 是否为升级方案            |
| isredeem    | boolean | 是否通过兑换码领取          |
| redeem_id   | string  | 兑换码id              |
| pay_type    | int     | 支付方式(类型),有待补充      |


