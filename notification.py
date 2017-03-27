import arrow
import argparse
import datetime
import json
import redis
from twilio.rest import TwilioRestClient

account = 'AC38e6a55ec14462e82a7e902c087dea1b'
token = 'aaa5f6806a17519c49f1f61a7a1f766d'
client = TwilioRestClient(account, token)

def send_notification(pattern, del_flag=False):
    redis_con = redis.Redis()
    get_keys = redis_con.keys(pattern)
    if del_flag:
        redis_con.delete(get_keys)
        return
    for each_time_key in get_keys:
        get_users_list = redis_con.hgetall(each_time_key)
        for each_user, each_data in get_users_list.items():
            import pdb; pdb.set_trace()
            if '1900-' not in each_time_key.decode('utf-8'):
                date = each_time_key[:10].decode('utf-8')
                notification_sent_flag = redis_con.hget(date, each_user)
                notification_sent_set = True
            else:
                date = each_time_key[5:15].decode('utf-8')
                notification_sent_flag = None
                notification_sent_set = False
            if not notification_sent_flag:
                hmdata = redis_con.hget('1900-%sT00:00:00+00:00'%(date), each_user)
                data_obj = json.loads(hmdata.decode('utf-8'))
                phone = data_obj['phone']
                time_list = data_obj['time']
                message = client.messages.create(
                    to='+1%s' % (phone, ),
                    from_='+12403033098',
                    body='Hello! Your appointment is at %s' % ('\n'.join(time_list)))
                if notification_sent_set:
                    notification_sent = redis_con.hset(date, each_user, 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send notifications')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--night', action='store_true')
    group.add_argument('-m', '--morning', action='store_true')
    args = parser.parse_args()
    if args.night:
        time_obj = arrow.utcnow() + datetime.timedelta(days=1)
        pattern = time_obj.format('1900-YYYY-MM-DDT00*')
        send_notification(pattern)
        time_obj = arrow.utcnow() + datetime.timedelta(days=-1)
        pattern = time_obj.format('*YYYY-MM-DD*')
        send_notification(pattern, del_flag=True)
    if args.morning:
        time_obj = arrow.utcnow()
        pattern = time_obj.format('1900-YYYY-MM-DDT00*')
        send_notification(pattern)
        time_obj = arrow.utcnow() + datetime.timedelta(days=-1)
        pattern = time_obj.format('*YYYY-MM-DD*')
        send_notification(pattern, del_flag=True)
    else:
        time_obj = arrow.utcnow() + datetime.timedelta(hours=2)
        pattern = time_obj.format('YYYY-MM-DDTHH:mm*')
        send_notification(pattern)
