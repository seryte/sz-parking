import argparse
from handler import Handler

def main():
    parser = argparse.ArgumentParser(description="Parking Reservation Tool")
    parser.add_argument('--oneid', required=True, help='One ID')
    parser.add_argument('--authorization', required=True, help='Authorization token')
    parser.add_argument('--xtoken', required=True, help='X Token')
    parser.add_argument('--cookie', required=True, help='Cookie')
    parser.add_argument('--auth', default=None, help='Auth')
    parser.add_argument('--source', default='', help='Source')
    parser.add_argument('--park', required=True, help='Park name')
    parser.add_argument('--parkname', required=True, help='Parking lot name')
    parser.add_argument('--carno', required=True, help='Car number')
    parser.add_argument('--phone', required=True, help='Phone number')
    parser.add_argument('--duration_min', type=int, default=50, help='Duration in minutes')

    args = parser.parse_args()

    hdlr = Handler(
        one_id=args.oneid,
        authorization=args.authorization,
        x_token=args.xtoken,
        cookie=args.cookie,
        auth=args.auth,
        source=args.source
    )

    result = hdlr.search_reservation()
    print(result)

    result = hdlr.reserve_until_timeout(
        park=args.park,
        park_name=args.parkname,
        car_no=args.carno,
        phone=args.phone,
        duration_min=args.duration_min
    )

    print(result)

if __name__ == "__main__":
    main()
