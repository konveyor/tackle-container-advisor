from collections import OrderedDict
import copy

class Test_check():

    def checkList(self, expected, actual, isRecursiveKeyCs):

        if len(expected) != len(actual):
            return False
        for ll in range(len(expected)):
            entryE = expected[ll]
            entryA = actual[ll]
            typeEentry = type(entryE)
            typeAentry = type(entryA)

            if typeEentry != typeAentry and typeEentry is not float and typeAentry is not float:
                return False
            if typeEentry is str:
                if entryE != "NA":
                   if entryE.endswith(":NA"):
                        indexE = entryE.rfind(":")
                        entryEprune = entryE[:indexE]
                        indexA = entryA.rfind(":")
                        entryAprune = entryA[:indexA]
                        if entryAprune != entryEprune:
                            return False
                   else:
                       if entryA != entryE:
                           return False
            elif typeEentry is dict:
                if self.checkDict(self, entryE, entryA, isRecursiveKeyCs, isRecursiveKeyCs) == False:
                    return False
            elif typeEentry is list:
                if self.checkList(self, entryE, entryA, isRecursiveKeyCs) == False:
                    return False
            elif typeAentry is float:
                return abs(entryE-entryA) < 0.05

            else:
               if entryA != entryE:
                  return False
        return True

    def checkDict(self,expected, actual, isKeyCs, isRecursiveKeyCs):
       newE = {}
       newA = {}
       if not isKeyCs:
          for (key,value) in expected.items():
             newKey = key.lower()
             newE[newKey] = value
          for (key,value) in actual.items():
             newKey = key.lower()
             newA[newKey] = value
       else:
          newE = copy.deepcopy(expected)
          newA = copy.deepcopy(actual)
       allEKeys = list(newE.keys())
       allAKeys = list(newA.keys())
       allEKeys.sort()
       allAKeys.sort()
       if allEKeys != allAKeys:
          return False
       for keyE in allEKeys:

          valueE = newE[keyE]
          valueA = newA[keyE]
          typeE = type(valueE)
          typeA = type(valueA)
          if typeE != typeA:
             return False
          if typeE is str:
             if valueE != "NA":
                if valueE.endswith(":NA"):
                     indexE = valueE.rfind(":")
                     valueEprune = valueE[:indexE]
                     indexA = valueA.rfind(":")
                     valueAprune = valueA[:indexA]
                     if valueAprune != valueEprune:
                         return False
                else:
                    if valueA != valueE:
                        return False
          elif typeE is dict:
             if self.checkDict(self, valueE, valueA, isRecursiveKeyCs, isRecursiveKeyCs) == False:
                 return False
          elif typeE is list:
             if self.checkList(self, valueE, valueA, isRecursiveKeyCs) == False:
                 return False
          else:
             if valueA != valueE:
                return False
       return True

    def checkEqual(self,expected, actual):
       if type(expected) != type(actual):
           return False
       if type(expected) != list:
           return False
       if(len(expected) != len(actual)):
          return False
       for i in range(len(expected)):
          myEOd = expected[i]
          myAOd = actual[i]

          if type(myEOd) is OrderedDict or type(myEOd) is dict:
              if self.checkDict(self, myEOd, myAOd, True, False) == False:
                  return False
          elif type(myEOd) is list:
              if self.checkList(self, myEOd, myAOd, False) == False:
                  return False
          else:
              return myEOd == myAOd
       return True
