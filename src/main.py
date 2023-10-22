#import functions_framework
import sqlalchemy
import pymysql
import os
from google.cloud import compute_v1
from google.cloud.sql.connector import Connector

PROJECT_ID = "ppetrov-internal-402521"
CONNECTION_NAME = "{}:us-east1:ex-zh-part2".format(PROJECT_ID)
DB_NAME = os.environ.get("DB_NAME", "default")
DB_USER = os.environ.get("DB_USER", "randomuser")
DB_PASS = os.environ.get("DB_PASS", "randompass")
TABLE_NAME = os.environ.get("TABLE_NAME", "randomtable")


def init_connection_pool(connector: Connector) -> sqlalchemy.engine.Engine:
    def getconn() -> pymysql.connections.Connection:
        conn = connector.connect(
            CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )
        return conn
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool


def sql_exec(sql_stmt):
    stmt = sqlalchemy.text(sql_stmt)
    with Connector() as connector:
        pool = init_connection_pool(connector)
        try:
            with pool.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        except Exception as e:
            return 'Error: {}'.format(str(e))
        return 'ok'


def insert(network, region, ip_cidr_range):
    sql_stmt = """
        INSERT INTO vpc_subnets (network, region, ip_cidr_ranges)
        SELECT * FROM (
            SELECT
                \"{net_val}\",
                \"{reg_val}\",
                \"{cidr_val}\"
        ) AS tmp_name
        WHERE NOT EXISTS (
            SELECT
                network,
                region,
                ip_cidr_ranges
            FROM
                vpc_subnets
            WHERE
                network = \"{net_val}\" AND
                region = \"{reg_val}\" AND
                ip_cidr_ranges = \"{cidr_val}\"
        ) LIMIT 1;
    """.format(net_val=network, reg_val=region, cidr_val=ip_cidr_range)

    return sql_exec(sql_stmt)


def delete(network, ips):
    sql_stmt = """
        DELETE FROM
            vpc_subnets
        WHERE
            network = \"{net_val}\" AND
            ip_cidr_ranges NOT IN ({ips});
    """.format(net_val=network, ips=ips)

    print(sql_stmt)
    return sql_exec(sql_stmt)


#@functions_framework.http
def run(request):

    vpc_ips = {}
    subnet_client = compute_v1.SubnetworksClient()
    request = compute_v1.ListUsableSubnetworksRequest(project=PROJECT_ID,)

    page_result = subnet_client.list_usable(request=request)
    for response in page_result:
        network = response.network.split("/")[-1]
        ip_cidr_range = response.ip_cidr_range
        region = response.subnetwork.split("/")[-3]

        print(insert(network, region, ip_cidr_range))

        vpc_ips.setdefault(network, [])
        vpc_ips[network].append(ip_cidr_range)

    for vpc, ips in vpc_ips.items():
        print(delete(vpc, "'" + "','".join(ips) + "'"))

    return "synced"
