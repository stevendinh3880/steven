import arrow
import argparse
import datetime
import redis
from twilio.rest import TwilioRestClient

account = 'AC38e6a55ec14462e82a7e902c087dea1b'
token = 'aaa5f6806a17519c49f1f61a7a1f766d'
client = TwilioRestClient(account, token)

def send_notification(pattern, del_flag=False):
    redis_con = redis.Redis()

    get_keys = redis_con.keys(pattern)
    for each_time_key in get_keys:
        time_obj = arrow.get(each_time_key.decode("utf-8")).format('YYYY-MM-DD HH:mm')
        get_users_list = redis_con.hgetall(each_time_key)
        for each_user, each_phone in get_users_list.items():
            message = client.messages.create(
                to='+1%s' % (each_phone.decode('utf-8')),
                from_='+12403033098',
                body='Hello! Your appointment is at %s' % (str(time_obj)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send notifications')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--daily', action='store_true')
    args = parser.parse_args()
    if args.daily:
        time_obj = arrow.utcnow() + datetime.timedelta(days=1)
        pattern = time_obj.format('YYYY-MM-DD*')
        send_notification(pattern)
    else:
        time_obj = arrow.utcnow() + datetime.timedelta(hours=2)
        pattern = time_obj.format('YYYY-MM-DDTHH:MM*')
        send_notification(pattern, del_flag=True)
