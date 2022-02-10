import math
import sys
import scipy as sp


def check_node_absorbing(edges, node):
    if node in edges.row:
        return False
    else:
        return True


def SparseMatrixAdd(A, B):
    """
            Calculate addition of matrix A and matrix B.

            :param sp.coo_matrix A: matrix A, B:matrix B
            :return: matrix result

            """
    row = []
    col = []
    data = []
    data_set = set()
    for i in range(len(A.data)):
        row.append(A.row[i])
        col.append(A.col[i])
        data_set.add((A.row[i], A.col[i]))
        data.append(A.data[i])
    for i in range(len(B.data)):
        if (B.row[i], B.col[i]) not in data_set:
            row.append(B.row[i])
            col.append(B.col[i])
            data.append(A.data[i])
        else:
            m = list(zip(row, col))
            n = m.index((B.row[i], B.col[i]))
            data[n] += B.data[i]
    mx = sp.coo_matrix((data, (row, col)), shape=(A.shape[0], A.shape[1]), dtype=int)
    return mx


def SparseMatrixMultiply(A, B):
    """
        Calculate product of matrix A and matrix B.

        :param sp.coo_matrix A: matrix A, B:matrix B
        :return: matrix result

        """
    row = []
    col = []
    data = []
    data_set = set()
    data_dict = dict()
    for i in range(len(A.col)):
        for j in range(len(B.row)):
            if A.col[i] == B.row[j]:
                if (A.row[i], B.col[j]) not in data_set:
                    data_set.add((A.row[i], B.col[j]))
                    data_dict[(A.row[i], B.col[j])] = A.data[i] * B.data[j]
                else:
                    data_dict[(A.row[i], B.col[j])] += A.data[i] * B.data[j]
    for key in data_dict.keys():
        row.append(key[0])
        col.append(key[1])
        data.append(data_dict[key])
    mx = sp.coo_matrix((data, (row, col)), shape=(A.shape[0], B.shape[1]), dtype=int)
    return mx


def MatrixMultiply(A, n):
    """
    Calculate n power of matrix A.

    :param sp.coo_matrix a: matrix A
    :param int n: n power
    :return: matrix result

    """
    result = sp.coo_matrix(
        ([1 for i in range(A.shape[0])], ([i for i in range(A.shape[0])], [i for i in range(A.shape[0])])),
        shape=(A.shape[0], A.shape[0]), dtype=int)
    for i in range(n):
        result = SparseMatrixMultiply(result, A)
    return result


class TransferProbability:
    def __init__(self, nodes, edges, traj, trajectories):
        self.nodes = nodes
        self.edges = edges
        self.traj = traj
        self.trajectories = trajectories
        self.vector = None
        self.derive()

    def derive(self):
        """
        Derive matrix P ,matrix Q ,matrix S and column vector V of each node.

        """
        self.vector = []
        for node in self.nodes:
            p = self.create_transition_matrix(node)
            q = self.reorganize(p, node)
            self.vector[node] = self.cal_vector(node, p, q)

    def create_transition_matrix(self, d):
        """
        Construct the transition matrix P by function transition_probability.

        :param Point d: the destination node
        :return: matrix P

        """
        nodes_len = len(self.nodes)
        p_row = []
        p_col = []
        p_data = []
        for row in range(nodes_len):
            for col in range(nodes_len):
                p = self.transition_probability(d, row, col)
                if p != 0:
                    p_row.append(row)
                    p_col.append(col)
                    p_data.append(p)
        p_mx = sp.coo_matrix((p_data, (p_row, p_col)), shape=(nodes_len, nodes_len), dtype=int)
        return p_mx

    def transition_probability(self, d, nodei, nodej):
        """
        Get the transition probability of moving from nodei to nodej
        through the state of nodei and the subscripts of both nodes.

        :param Point d: the destination node
        :param Point nodei: the starting node of transition
        :param Point nodej: the ending node of transition
        :return: the transition probability

        """

        if (nodei == d or check_node_absorbing(self.edges, nodei) == True) \
                and nodei == nodej:
            return 1
        elif (not (nodei == d or check_node_absorbing(self.edges, nodei) == True)) \
                and nodei != nodej:
            return self.prd(d, nodei, nodej)
        else:
            return 0

    def prd(self, d, nodei, nodej):
        """
        Get the turning probability of moving from nodei to nodej
        through the ratio of adding func values of all the trajectories
        on (nodei,nodej) and all the trajectories starting from nodei.

        :param Point d: the destination node
        :param Point nodei: the starting node of transition
        :param Point nodej: the ending node of transition
        :return: the turning probability

        """
        sum_ij, sum_i = 0, 0

        # add func values of all the trajectories on (nodei,nodej)
        if (nodei, nodej) in self.traj:
            for t in self.traj[(nodei, nodej)]:
                sum_ij += self.func(t, d, nodei)

        # add func values of all the trajectories starting from nodei
        for col in range(len(self.nodes)):
            if (nodei, col) in self.traj:
                for t in self.traj[(nodei, col)]:
                    sum_i += self.func(t, d, nodei)

        if sum_i == 0:
            return 0
        return sum_ij / sum_i

    def func(self, traj, d, nodei):
        """
        Estimate the likelihood that a trajectory traj might
        suggest a correct route to d.

        :param Point.trajectory_id traj: the trajectory
        :param Point d: the destination node
        :param Point nodei: the starting node
        :return: the likelihood

        """
        dists = sys.maxsize
        flag = 0
        traj_value = self.trajectories[traj]
        nodei_index_in_traj = \
            self.trajectories[traj].index(nodei)

        # trajectory traj passes node d ,dists = 0
        if d in traj_value[nodei_index_in_traj::]:
            dists = 0
            flag = 1
        # trajectory traj only has one node rather than edge
        elif len(traj_value[nodei_index_in_traj::]) == 1:
            dists = math.pow(
                ((self.nodes[d][0] - self.nodes[traj_value[0]][0]) ** 2
                 + (self.nodes[d][1] - self.nodes[traj_value[0]][1]) ** 2),
                0.5)
            flag = 1
        # trajectory traj has one edge at least
        elif len(traj_value[nodei_index_in_traj::]) >= 2:
            for index in range(nodei_index_in_traj, len(traj_value) - 1):
                new_dist = self.get_dist(d, traj_value[index], traj_value[index + 1])
                if new_dist < dists:
                    dists = new_dist
                    flag = 1

        if flag == 0:
            return 0
        return math.exp(-dists)

    def get_dist(self, d, point1, point2):
        """
        Get the shortest Euclidean/network distance between d and
        the segment from point1 to point2.

        :param Point d: the point outside the segment
        :param Point point1: the endpoint of the segment
        :param Point point2: another endpoint of the segment
        :return: the distance

        """
        d_x = self.nodes[d][0]
        d_y = self.nodes[d][1]
        point1_x = self.nodes[point1][0]
        point1_y = self.nodes[point1][1]
        point2_x = self.nodes[point2][0]
        point2_y = self.nodes[point2][1]
        cross = (point2_x - point1_x) * (d_x - point1_x) \
                + (point2_y - point1_y) * (d_y - point1_y)
        dist2 = (point2_x - point1_x) ** 2 + (point2_y - point1_y) ** 2

        if cross <= 0:
            return math.sqrt((d_x - point1_x) ** 2 + (d_y - point1_y) ** 2)
        if cross >= dist2:
            return math.sqrt((d_x - point2_x) ** 2 + (d_y - point2_y) ** 2)
        r = cross / dist2
        p_x = point1_x + (point2_x - point1_x) * r
        p_y = point1_y + (point2_y - point1_y) * r
        return math.sqrt((d_x - p_x) ** 2 + (d_y - p_y) ** 2)

    def reorganize(self, p, d):
        """
        Reorganize matrix P to canonical form by grouping
        absorbing states into ABS and transient states into TR.

        :param np.array p: matrix P
        :param Point d: the destination node
        :return: matrix Q(TR * TR), matrix S(TR * ABS)

        """
        ABS = []
        TR = []
        for node in self.nodes:
            if node == d or check_node_absorbing(p, node) == True:
                ABS.append(node)
            else:
                TR.append(node)

        m = list(zip(p.row, p.col))
        row = []
        col = []
        data = []
        for i in range(len(TR)):
            for j in range(len(TR)):
                if (TR[i], TR[j]) in m:
                    n = m.index((TR[i], TR[j]))
                    row.append(i)
                    col.append(j)
                    data.append(p.data[n])
                else:
                    continue
        p_left_top = sp.coo_matrix((data, (row, col)), shape=(len(TR), len(TR)), dtype=int)
        return p_left_top

    def cal_vector(self, d, p, q):
        """
        Get the column vector V of each node through matrix P and matrix Q.

        :param Point d: the node d
        :param np.array p: matrix P
        :param np.array q: matrix Q
        :return: column vector V

        """
        TR = []
        ABS = []

        # D=S[*,d]
        for node in self.nodes:
            if not (node == d or check_node_absorbing(p, node) == True):
                TR.append(node)
            else:
                ABS.append(node)

        m = list(zip(p.row, p.col))
        row = []
        col = []
        data = []
        for i in range(len(TR)):
            if (TR[i], d) in m:
                n = m.index((TR[i], d))
                row.append(i)
                col.append(1)
                data.append(p.data[n])
            else:
                continue
        D = sp.coo_matrix((data, (row, col)), shape=(len(TR), 1), dtype=int)

        # V=D+Q·D+Q^2·D+...+Q^(t-1)·D
        v = sp.coo_matrix(([], ([], [])), shape=(len(TR), 1), dtype=int)
        for j in range(0, sys.maxsize):
            v = SparseMatrixAdd(v, SparseMatrixMultiply(MatrixMultiply(q, j), D))

        row = v.row
        col = v.col
        for m in range(len(TR)):
            row[m] = TR[row[m]]
        v = sp.coo_matrix((v.data, (row, col)), shape=(len(self.nodes), 1), dtype=int)
        return v