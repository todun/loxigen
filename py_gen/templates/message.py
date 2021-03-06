:: # Copyright 2013, Big Switch Networks, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http::: #www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: import itertools
:: import of_g
:: include('_copyright.py')

:: include('_autogen.py')

import struct
import loxi
import const
import common
import action # for unpack_list
:: if version >= 2:
import instruction # for unpack_list
:: #endif
:: if version >= 4:
import meter_band # for unpack_list
:: #endif
import util
import loxi.generic_util

class Message(object):
    version = const.OFP_VERSION
    type = None # override in subclass
    xid = None

:: for ofclass in ofclasses:
:: from py_gen.codegen import Member, LengthMember, TypeMember
:: normal_members = [m for m in ofclass.members if type(m) == Member]
:: type_members = [m for m in ofclass.members if type(m) == TypeMember]
class ${ofclass.pyname}(Message):
:: for m in type_members:
    ${m.name} = ${m.value}
:: #endfor

    def __init__(self, ${', '.join(["%s=None" % m.name for m in normal_members])}):
        self.xid = xid
:: for m in [x for x in normal_members if x.name != 'xid']:
        if ${m.name} != None:
            self.${m.name} = ${m.name}
        else:
            self.${m.name} = ${m.oftype.gen_init_expr()}
:: #endfor

    def pack(self):
        packed = []
:: include('_pack.py', ofclass=ofclass)
        return ''.join(packed)

    @staticmethod
    def unpack(buf):
        if len(buf) < 8: raise loxi.ProtocolError("buffer too short to contain an OpenFlow message")
        obj = ${ofclass.pyname}()
:: include('_unpack.py', ofclass=ofclass)
        return obj

    def __eq__(self, other):
        if type(self) != type(other): return False
        if self.version != other.version: return False
        if self.type != other.type: return False
:: for m in normal_members:
        if self.${m.name} != other.${m.name}: return False
:: #endfor
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.show()

    def show(self):
        import loxi.pp
        return loxi.pp.pp(self)

    def pretty_print(self, q):
:: include('_pretty_print.py', ofclass=ofclass)

:: #endfor

def parse_header(buf):
    if len(buf) < 8:
        raise loxi.ProtocolError("too short to be an OpenFlow message")
    return struct.unpack_from("!BBHL", buf)

def parse_message(buf):
    msg_ver, msg_type, msg_len, msg_xid = parse_header(buf)
    if msg_ver != const.OFP_VERSION and msg_type != ofp.OFPT_HELLO:
        raise loxi.ProtocolError("wrong OpenFlow version")
    if len(buf) != msg_len:
        raise loxi.ProtocolError("incorrect message size")
    if msg_type in parsers:
        return parsers[msg_type](buf)
    else:
        raise loxi.ProtocolError("unexpected message type")

:: # TODO fix for OF 1.1+
def parse_flow_mod(buf):
    if len(buf) < 56 + 2:
        raise loxi.ProtocolError("message too short")
    cmd, = struct.unpack_from("!H", buf, 56)
    if cmd in flow_mod_parsers:
        return flow_mod_parsers[cmd](buf)
    else:
        raise loxi.ProtocolError("unexpected flow mod cmd %u" % cmd)

:: if version < of_g.VERSION_1_3:
def parse_stats_reply(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    stats_type, = struct.unpack_from("!H", buf, 8)
    if stats_type in stats_reply_parsers:
        return stats_reply_parsers[stats_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats type %u" % stats_type)

def parse_stats_request(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    stats_type, = struct.unpack_from("!H", buf, 8)
    if stats_type in stats_request_parsers:
        return stats_request_parsers[stats_type](buf)
    else:
        raise loxi.ProtocolError("unexpected stats type %u" % stats_type)
:: else:
def parse_multipart_reply(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    multipart_type, = struct.unpack_from("!H", buf, 8)
    if multipart_type in multipart_reply_parsers:
        return multipart_reply_parsers[multipart_type](buf)
    else:
        raise loxi.ProtocolError("unexpected multipart type %u" % multipart_type)

def parse_multipart_request(buf):
    if len(buf) < 8 + 2:
        raise loxi.ProtocolError("message too short")
    multipart_type, = struct.unpack_from("!H", buf, 8)
    if multipart_type in multipart_request_parsers:
        return multipart_request_parsers[multipart_type](buf)
    else:
        raise loxi.ProtocolError("unexpected multipart type %u" % multipart_type)
:: #endif

:: if version == of_g.VERSION_1_0:
def parse_vendor(buf):
:: else:
def parse_experimenter(buf):
:: #endif
    if len(buf) < 16:
        raise loxi.ProtocolError("experimenter message too short")

    experimenter, = struct.unpack_from("!L", buf, 8)
    if experimenter == 0x005c16c7: # Big Switch Networks
        subtype, = struct.unpack_from("!L", buf, 12)
    elif experimenter == 0x00002320: # Nicira
        subtype, = struct.unpack_from("!L", buf, 12)
    else:
        raise loxi.ProtocolError("unexpected experimenter id %#x" % experimenter)

    if subtype in experimenter_parsers[experimenter]:
        return experimenter_parsers[experimenter][subtype](buf)
    else:
        raise loxi.ProtocolError("unexpected experimenter %#x subtype %#x" % (experimenter, subtype))

parsers = {
:: sort_key = lambda x: x.type_members[1].value
:: msgtype_groups = itertools.groupby(sorted(ofclasses, key=sort_key), sort_key)
:: for (k, v) in msgtype_groups:
:: v = list(v)
:: if len(v) == 1:
    ${k} : ${v[0].pyname}.unpack,
:: else:
    ${k} : parse_${k[11:].lower()},
:: #endif
:: #endfor
}

flow_mod_parsers = {
    const.OFPFC_ADD : flow_add.unpack,
    const.OFPFC_MODIFY : flow_modify.unpack,
    const.OFPFC_MODIFY_STRICT : flow_modify_strict.unpack,
    const.OFPFC_DELETE : flow_delete.unpack,
    const.OFPFC_DELETE_STRICT : flow_delete_strict.unpack,
}

:: if version < of_g.VERSION_1_3:
stats_reply_parsers = {
    const.OFPST_DESC : desc_stats_reply.unpack,
    const.OFPST_FLOW : flow_stats_reply.unpack,
    const.OFPST_AGGREGATE : aggregate_stats_reply.unpack,
    const.OFPST_TABLE : table_stats_reply.unpack,
    const.OFPST_PORT : port_stats_reply.unpack,
    const.OFPST_QUEUE : queue_stats_reply.unpack,
:: if version < of_g.VERSION_1_1:
    const.OFPST_VENDOR : experimenter_stats_reply.unpack,
:: else:
    const.OFPST_EXPERIMENTER : experimenter_stats_reply.unpack,
:: #endif
:: if version >= of_g.VERSION_1_1:
    const.OFPST_GROUP : group_stats_reply.unpack,
    const.OFPST_GROUP_DESC : group_desc_stats_reply.unpack,
:: #endif
:: if version >= of_g.VERSION_1_2:
    const.OFPST_GROUP_FEATURES : group_features_stats_reply.unpack,
:: #endif
}

stats_request_parsers = {
    const.OFPST_DESC : desc_stats_request.unpack,
    const.OFPST_FLOW : flow_stats_request.unpack,
    const.OFPST_AGGREGATE : aggregate_stats_request.unpack,
    const.OFPST_TABLE : table_stats_request.unpack,
    const.OFPST_PORT : port_stats_request.unpack,
    const.OFPST_QUEUE : queue_stats_request.unpack,
:: if version < of_g.VERSION_1_1:
    const.OFPST_VENDOR : experimenter_stats_request.unpack,
:: else:
    const.OFPST_EXPERIMENTER : experimenter_stats_request.unpack,
:: #endif
:: if version >= of_g.VERSION_1_1:
    const.OFPST_GROUP : group_stats_request.unpack,
    const.OFPST_GROUP_DESC : group_desc_stats_request.unpack,
:: #endif
:: if version >= of_g.VERSION_1_2:
    const.OFPST_GROUP_FEATURES : group_features_stats_request.unpack,
:: #endif
}
:: else:
# TODO OF 1.3 multipart messages
:: #endif

:: experimenter_ofclasses = [x for x in ofclasses if x.type_members[1].value == 'const.OFPT_VENDOR']
:: sort_key = lambda x: x.type_members[2].value
:: experimenter_ofclasses.sort(key=sort_key)
:: grouped = itertools.groupby(experimenter_ofclasses, sort_key)
experimenter_parsers = {
:: for (experimenter, v) in grouped:
    ${experimenter} : {
:: for ofclass in v:
        ${ofclass.type_members[3].value}: ${ofclass.pyname}.unpack,
:: #endfor
    },
:: #endfor
}
