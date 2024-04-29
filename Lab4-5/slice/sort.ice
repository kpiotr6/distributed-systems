
module sorting
{
  enum Ordering { ASCENDING, DESCENDING };

  ["java:type:java.util.LinkedList<Long>"]
  sequence<long> LongList;
  ["java:type:java.util.LinkedList<String>"]
  sequence<string> StringList;

  interface Sort
  {
    void sortList(Ordering ordering);
    void setList(LongList seq);
    LongList getList();
  };

  interface SortDefault
  {
    LongList sortList(Ordering ordering, LongList toSort);
  }
  interface ObjectManager
  {
    StringList listObjects();
    void destroy(string category, string name);
  }

};
