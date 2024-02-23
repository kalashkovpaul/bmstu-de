from math import floor

from generator import Generator
from handler import Handler

generation = 0
handling = 1

time = 0
state = 1
data = 2

delta = 1e-5

class System:
    def __init__(self, a1, b1, a2, b2, msg_num, model_time):
        self.messages_amount = msg_num
        self.step = 0.001
        self.model_time = model_time
        self.generator = Generator(a1, b1)
        self.handler = Handler(a2, b2)

    def delta_t(self):
        processed_amount = 0
        self.handler.free = True

        handling_time = 0
        current_time = self.step
        generated_time = 0
        previous_generated_time = 0
        queue = []
        waiting_times = []

        i1_actuals = []
        i2_actuals = []
        generated_in_period = 0
        processed_in_period = 0
        current_period = 0


        while processed_amount < self.messages_amount and current_time < self.model_time:
            if current_time > generated_time:
                queue.append(current_time)

                generated_in_period += 1

                previous_generated_time = generated_time
                generated_time += self.generator.get_time_interval()

            if current_time > handling_time:
                if len(queue):
                    handler_was_free = self.handler.free
                    if self.handler.free:
                        self.handler.free = False
                    else:
                        processed_amount += 1
                        processed_in_period += 1

                        enter_time = queue.pop(0)
                        waiting_times.append(current_time - enter_time)
                    if handler_was_free:
                        handling_time = previous_generated_time + self.handler.get_time_interval()
                    else:
                        handling_time += self.handler.get_time_interval()
                else:
                    self.handler.free = True
            current_time += self.step
            if floor(current_time) != current_period:
                current_period = floor(current_time)
                i1_actuals.append(generated_in_period)
                generated_in_period = 0
                i2_actuals.append(processed_in_period)
                processed_in_period = 0


        avg_in_wait = sum(waiting_times) / len(waiting_times)
        avg_i1 = 0
        avg_i2 = 0
        if len(i1_actuals):
            avg_i1 = sum(i1_actuals) / len(i1_actuals)
        if len(i2_actuals):
            avg_i2 = sum(i2_actuals) / len(i2_actuals)
        return avg_in_wait, avg_i1, avg_i2


    def event_driven(self):
        max_length = 0
        queue_length = 0
        processed_amounts = 0
        processed = False
        self.handler.free = True
        waiting_times = []
        current_period = 0

        initial_time = self.generator.get_time_interval()
        events = [[initial_time, generation, initial_time]]
        i1_actuals = []
        i2_actuals = []
        generated_in_period = 0
        processed_in_period = 0
        current_period = 0

        prev_avg_in_wait = 0
        while True:
            event = events.pop(0)

            if event[state] == generation:
                queue_length += 1
                generated_in_period += 1
                if queue_length > max_length:
                    max_length = queue_length
                next_time = event[time] + self.generator.get_time_interval()
                self.__insert_event(events, [next_time, generation, event[time]])
                if self.handler.free:
                    processed = True

            if event[state] == handling:
                waiting_times.append(event[time] - event[data])
                processed_amounts += 1
                processed_in_period += 1
                processed = True

            if processed:
                if queue_length > 0:
                    queue_length -= 1
                    self.__insert_event(events, [event[time] + self.handler.get_time_interval(), handling, event[data]])
                    self.handler.free = False
                else:
                    self.handler.free = True

                processed = False
            if floor(event[time]) != current_period:
                current_period = floor(event[time])
                i1_actuals.append(generated_in_period)
                generated_in_period = 0
                i2_actuals.append(processed_in_period)
                processed_in_period = 0
            if self.model_time and event[time] > self.model_time:
                break
        avg_in_wait = sum(waiting_times) / len(waiting_times)
        avg_i1 = 0
        avg_i2 = 0
        if len(i1_actuals):
            avg_i1 = sum(i1_actuals) / len(i1_actuals)
        if len(i2_actuals):
            avg_i2 = sum(i2_actuals) / len(i2_actuals)
        return avg_in_wait, avg_i1, avg_i2

    def __insert_event(self, events, event):
        i = 0
        while i < len(events) and events[i][time] < event[time]:
              i += 1
        if 0 < i < len(events):
            events.insert(i - 1, event)
        else:
            events.insert(i, event)