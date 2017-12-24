from platypush.message.event import Event, EventMatchResult


class FlicButtonEvent(Event):
    """ Flic button event """

    def __init__(self, btn_addr, sequence, *args, **kwargs):
        super().__init__(btn_addr=btn_addr, sequence=sequence, *args, **kwargs)


    def matches_condition(self, condition):
        result = EventMatchResult(is_match=False)

        if not isinstance(self, condition.type) \
                or self.args['btn_addr'] != condition.args['btn_addr']:
            return result

        cond_sequence = list(condition.args['sequence'])
        event_sequence = list(self.args['sequence'])

        while cond_sequence and event_sequence:
            cond_press = cond_sequence[0]
            event_press = event_sequence[0]

            if cond_press == event_press:
                cond_sequence.pop(0)
                result.score += 1

            event_sequence.pop(0)

        result.is_match = len(cond_sequence) == 0
        return result


# vim:sw=4:ts=4:et:

