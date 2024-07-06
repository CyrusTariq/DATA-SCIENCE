from aiokafka import AIOKafkaProducer
import asyncio

async def send_one(mg):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait("topic_test", mg.encode('utf-8'))
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

def send_msg(mg):
    asyncio.run(send_one(mg))
#asyncio.run(send_one(mg))