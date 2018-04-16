# Command Cheat Sheet

```console
make flask_shell
```

```python
mywebhook = Webhook(name='test endpoint', endpoint_url='http://web:5000/receive_notifications', active=True)
db.session.add(mywebhook)
db.session.commit()
```
