import numpy as np
import itertools

class Landscape:
    
    def __init__(self, row, col, ls):
        self.ROW = row
        self.COL = col
        self.landscape = ls
        
    def inBounds(self, i, j):
        '''checks if cell is inbounds'''
        return (i >= 0 and i < self.ROW and
                j >= 0 and j < self.COL)
    
    def isSafe(self, i, j, visited):
        '''checks if cell is inbounds, previously visited, and valid number'''
        return (self.inBounds(i,j) and
                not visited[i][j] and self.landscape[i][j])
    
    def findNode(self, i, j, visited, nodeName=1):
        '''recursive function that finds all cells in a particular node (8-neighbor)'''
        '''records visitation to each cell'''
        '''(optional) provides node ID by renaming all cells in the node'''
        rowNbr = [-1, -1, -1, 0, 0, 1, 1, 1];
        colNbr = [-1, 0, 1, -1, 1, -1, 0, 1];
        visited[i][j] = True
        self.landscape[i][j] = nodeName
        for k in range(8):
            if self.isSafe(i + rowNbr[k], j + colNbr[k], visited):
                self.findNode(i + rowNbr[k], j + colNbr[k], visited, nodeName=nodeName) 
        return nodeName + 1
    
    def renameNode(self):
        '''finds all nodes and renames each with unique node ID'''
        visited = [[False for j in range(self.COL)]for i in range(self.ROW)]
        nodeName = 1
        for i in range(self.ROW):
            for j in range(self.COL):
                if visited[i][j] == False and self.landscape[i][j] == 1:
                    nodeName = self.findNode(i, j, visited, nodeName)
                    
    def nbrNodes(self):
        '''returns total number of nodes in landscape'''
        self.renameNode()
        nodes = np.max(self.landscape)
        return nodes
    
    def sizes(self):
        '''returns dictionary of node sizes'''
        self.renameNode()
        pNbr, pSize = np.unique(self.landscape[self.landscape>0],return_counts=True)
        sizes = dict(zip(pNbr,pSize))
        return sizes
    
    def findLink(self, i, j, visited, minHabitat, maxDispDist):
        '''finds nodes meeting min habitat and max dispersal distance reqs (from given cell)'''
        visited[i][j] = True
        coordNbr = list(range(-maxDispDist - 1,maxDispDist + 2))
        coord = list(itertools.product(coordNbr, repeat=2))
        coord.remove((0,0))
        habSize = self.sizes()
        link = []
        for k in range(len(coord)):
            if self.isSafe(i + coord[k][0],j + coord[k][1], visited) and \
            self.landscape[i + coord[k][0]][j + coord[k][1]] > 0 and \
            self.landscape[i + coord[k][0]][j + coord[k][1]] != self.landscape[i][j] and \
            habSize[self.landscape[i + coord[k][0]][j + coord[k][1]]] >= minHabitat:
                link.append(self.landscape[i + coord[k][0]][j + coord[k][1]])
        link = np.unique(link)
        return link

    def links(self, minHabitat, maxDispDist):
        '''returns set of (node,node) pairs representing all links meeting min habitat and max dispersal distance reqs'''
        self.renameNode()
        visited = [[False for j in range(self.COL)]for i in range(self.ROW)]
        allLinks = set()
        habSize = self.sizes()
        for i in range(self.ROW):
            for j in range(self.COL):
                if visited[i][j] == False and \
                self.landscape[i][j] > 0 and \
                habSize[self.landscape[i][j]] >= minHabitat:
                    link = self.findLink(i,j,visited,minHabitat,maxDispDist)
                    for k in link:
                        if (k,self.landscape[i][j]) not in allLinks:
                            allLinks.add((self.landscape[i][j],k))
        return allLinks
    
    def linkDensity(self, minHabitat, maxDispDist):
        '''calculates link density of landscape given min habitat and max dispersal distance reqs'''
        L = len(self.links(minHabitat,maxDispDist))
        n = len(np.unique(list(self.links(minHabitat,maxDispDist))))
        ld = L/(n*(n-1)/2)
        return ld
         
    def findComponentArea(self,k,visited,links,nodes):
        '''returns the area of the visited component'''
        visited[k] = True
        nodes.add(links[k][0])
        nodes.add(links[k][1])
        size = self.sizes()
        for link in links:
            if visited[links.index(link)] == False and \
            (link[0] == links[k][0] or link[0] == links[k][1] or \
            link[1] == links[k][0] or link[1] == links[k][1]):
                self.findComponentArea(links.index(link),visited,links,nodes)
        nodes = list(nodes)
        area = []
        for node in nodes:
            area.append(size.get(node))
        return np.sum(area)   
    
    def largestComponent(self, minHabitat, maxDispDist):
        '''calculates largest component index given min habitat and max dispersal distance reqs'''
        links = list(self.links(minHabitat,maxDispDist))
        size = self.sizes()
        totalArea = []
        for n in size:
            if size[n] >= minHabitat:
                totalArea.append(size[n])
        totalArea = np.sum(totalArea)
        visited = [False for i in range(len(links))]
        componentArea = []
        for k in range(len(links)):
            if visited[k] == False:
                nodes = set()
                componentArea.append(self.findComponentArea(k,visited,links,nodes))
        return np.max(componentArea)/totalArea