#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import csv
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from bitcoinrpc.authproxy import AuthServiceProxy
from bitcoin.core import serialize as ser

mainnet = {
    'rpc_user': 'bitcoinrpc',
    'rpc_password': '123456',
    'rpc_host': '127.0.0.1',
    'rpc_port': 7116,
    'fork_height': 495867,
    'pow_limit': 0x0000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffff
}

testnet = {
    'rpc_user': 'bitcoinrpc',
    'rpc_password': '123456',
    'rpc_host': '127.0.0.1',
    'rpc_port': 17116,
    'fork_height': 1065121,
    'pow_limit': 0x00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff
}

regtest = {
    'rpc_user': 'user',
    'rpc_password': 'pass',
    'rpc_host': '127.0.0.1',
    'rpc_port': 16101,
    'fork_height': 1,
    'pow_limit': 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
}

net = None

bitcoinrpc = None
file_name = 'blocks.csv'


def set_net_type(network):
    global bitcoinrpc
    global net
    if network == 'mainnet':
        net = mainnet
    elif network == 'testnet':
        net = testnet
    elif network == 'regtest':
        net = regtest
    else:
        return
    bitcoinrpc = AuthServiceProxy("http://%s:%s@%s:%s" % (net['rpc_user'], net['rpc_password'], net['rpc_host'], net['rpc_port']))


def time_stamp_to_string(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


def get_block(height):
    block_hash = bitcoinrpc.getblockhash(height)
    return bitcoinrpc.getblock(block_hash)


def get_lastest_blocks(count, step=1):
    chain_info = bitcoinrpc.getblockchaininfo()
    block_height = chain_info['blocks']
    block_list = []
    for height in range(block_height - count*step, block_height + 1, step):
        block_list.append(get_block(height))
        print('block %s got' % height)
        time.sleep(0.2)
    return block_list


def get_blocks(from_height, to_height):
    block_list = []
    for height in range(from_height, to_height+1):
        block_list.append(get_block(height))
        print('block %s got' % height)
        time.sleep(0.2)
    return block_list


def write_blocks_to_csv(block_list):
    with open(file_name, 'w', newline='') as csv_file:
        file_header = ['height', 'difficulty', 'time', 'mediantime', 'nbits']
        writer = csv.writer(csv_file)
        writer.writerow(file_header)
        for block in block_list:
            writer.writerow([block['height'], block['difficulty'], block['time'], block['mediantime'], block['bits']])


def read_blocks_from_csv():
    block_list = []
    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            block = {
                'height': int(row[0]),
                'difficulty': float(row[1]),
                'time': int(row[2]),
                'mediantime': int(row[3]),
                'nbits': int(row[4], 16)
            }
            block_list.append(block)
    return block_list


def draw_solve_time_diagram(block_list):
    height_list = []
    solve_time_list = []
    for i in range(1, len(block_list)):
        height_list.append(block_list[i]['height'])
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)

    # plt.subplot(211)
    plt.plot(height_list, solve_time_list, marker='o', label='solve time diagram')
    plt.xlabel('height')
    plt.ylabel('solve time/minutes')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

    # x = []
    # y = []
    # solve_time_array = numpy.array(solve_time_list)
    # for i in range(3):
    #     count = ((i*5 <= solve_time_array) & (solve_time_array < (i+1)*5)).sum()
    #     if count == 0:
    #         continue
    #     x.append(i*5)
    #     y.append(count)
    # count = ((i+1) * 5 <= solve_time_array).sum()
    # if count != 0:
    #     x.append((i+1)*5)
    #     y.append(count)
    #
    # plt.subplot(212)
    # plt.bar([i + 2.5 for i in x], y, width=2.5)
    # plt.xlabel('solve time')
    # plt.ylabel('blocks')
    # ax = plt.gca()
    # ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    #
    # plt.subplots_adjust(wspace=0, hspace=0.4)

    plt.show()


def draw_difficulty_diagram(block_list):
    height_list = []
    difficulty_list = []
    for i in range(1, len(block_list)):
        height_list.append(block_list[i]['height'])
        difficulty_list.append(block_list[i]['difficulty'])
    plt.plot(height_list, difficulty_list, marker='o', label='difficulty changes')
    plt.xlabel('height')
    plt.ylabel('difficulty')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.show()


def draw_solve_time_pie(block_list):
    solve_time_list = []
    for i in range(1, len(block_list)):
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)

    x = []
    labels = []
    solve_time_array = numpy.array(solve_time_list)
    for i in range(3):
        count = ((i*5 <= solve_time_array) & (solve_time_array < (i+1)*5)).sum()
        if count == 0:
            continue
        x.append(count)
        labels.append('%s~%s minutes' % (i * 5, (i + 1) * 5))
    count = ((i+1) * 5 <= solve_time_array).sum()
    if count != 0:
        x.append(count)
        labels.append('>%s minutes' % ((i + 1) * 5))

    plt.pie(x, labels=labels, autopct='%3.1f %%')
    plt.show()


def nbits(num):
    # Convert integer to hex
    hexstr = format(num, 'x')
    first_byte, last_bytes = hexstr[0:2], hexstr[2:]
    # convert bytes back to int
    first, last = int(first_byte, 16), int(last_bytes, 16)
    return last * 256 ** (first - 3)


def difficulty(num):
    # Difficulty of genesis block / current
    return 0x00ffff0000000000000000000000000000000000000000000000000000 / nbits(num)


def get_next_work_required(block_list):
    global net
    fork_height = net['fork_height']
    adjust_interval = 72
    last_height = block_list[-1]['height']
    height_span = last_height + 1 - fork_height

    if height_span % adjust_interval != 0:
        print('Not time to adjust target.')
        return block_list[-1]['nbits']

    target_time_span = 72 * 10 * 60
    retarget_factor = 2
    real_time_span = block_list[-1]['time'] - block_list[-adjust_interval]['time']
    adjusted_time_span = real_time_span
    if adjusted_time_span < target_time_span//retarget_factor:
        adjusted_time_span = target_time_span//retarget_factor
    if adjusted_time_span > target_time_span*retarget_factor:
        adjusted_time_span = target_time_span*retarget_factor

    print('adjusted time span: %s, real time span: %s' % (adjusted_time_span, real_time_span))

    pow_limit = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    last_target = ser.uint256_from_compact(block_list[-1]['nbits'])
    next_target = last_target * adjusted_time_span // target_time_span

    if next_target > pow_limit:
        print('exceed pow limit')
        next_target = pow_limit

    next_nbits = ser.compact_from_uint256(next_target)
    print('original nbits:', hex(next_nbits))
    print('difficulty:', difficulty(next_nbits))

    return next_nbits


# next_target = avg_target * LWMA(solvetimes) / T
# next_target = (sum_target / N) * (weighted_solvetime_sum / (N*(N+1)/2)) / T
def lwma_next_work_required(block_list):

    # T
    target_solvetime = 10 * 60
    # N For T=600, 300, 150 use approximately N=60, 90, 120
    average_window = 60
    # Define a k that will be used to get a proper average after weighting the solvetimes.
    k = int(average_window * (average_window + 1) * target_solvetime // 2)

    height = block_list[-1]['height']
    pow_limit = net['pow_limit']

    # New coins should just give away first N blocks before using this algorithm.
    if height < average_window:
        return ser.compact_from_uint256(pow_limit)

    average_target = 0
    prev_timestamp = block_list[-average_window-1]['time']
    sum_weighted_solvetimes = 0
    solvetime_weight = 0

    # Loop through N most recent blocks.
    for i in range(height+1-average_window, height+1):
        block = block_list[i-height-1]
        # Prevent solvetimes from being negative in a safe way. It must be done like this.
        # In particular, do not attempt anything like  if(solvetime < 0) {solvetime=0;}
        # The +1 ensures new coins do not calculate nextTarget = 0.
        this_timestamp = block['time'] if block['time'] > prev_timestamp else prev_timestamp + 1

        # A 6*T limit will prevent large drops in difficulty from long solvetimes.
        solve_time = min(6*target_solvetime, this_timestamp-prev_timestamp)

        # The following is part of "preventing negative solvetimes".
        prev_timestamp = this_timestamp

        # Give linearly higher weight to more recent solvetimes.
        solvetime_weight = solvetime_weight + 1
        sum_weighted_solvetimes += solve_time * solvetime_weight

        target = ser.uint256_from_compact(block['nbits'])
        average_target += target // (average_window * k)  # Dividing by k here prevents an overflow below.

    # Desired equation in next line was nextTarget = avgTarget * sumWeightSolvetimes / k
    # but 1/k was moved to line above to prevent overflow in new coins
    next_target = sum_weighted_solvetimes * average_target

    if next_target > pow_limit:
        print('exceed pow limit')
        next_target = pow_limit

    next_nbits = ser.compact_from_uint256(next_target)
    print('lwma nbits:', hex(next_nbits))
    print('difficulty:', difficulty(next_nbits))

    return next_nbits


# set_net_type('regtest')

# write_blocks_to_csv(get_lastest_blocks(100))
# write_blocks_to_csv(get_blocks(288, 315))

# get_next_work_required(read_blocks_from_csv())
# lwma_next_work_required(read_blocks_from_csv())

# draw_solve_time_diagram(read_blocks_from_csv())
# draw_difficulty_diagram(read_blocks_from_csv())
# draw_solve_time_pie(read_blocks_from_csv())
