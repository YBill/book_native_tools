import 'dart:async';

import 'package:BookSummary/utils/LogUtil.dart';

class LyricController {

  /// 自动检测语言并选择断句方式
  /// 如果是中文使用 splitTextZh，否则使用 splitTextEn
  List<List<String>> splitText(String text) {
    if (isChineseText(text)) {
      return splitTextZh(text);
    } else {
      return splitTextEn(text);
    }
  }

  /// 通过下面算法来分割歌词（英文）
  /// 先通过\n\n来分割段落,然后通过(?<=[.,!?])\s+来分割句子
  /// 注意服务端返回的lrc必须跟这里算法保持一致，否则显示会有问题
  /// 原因是为了精确找到某一个词的位置，通过词找可能会有多个，然后现在是服务端切割和这里切割一致，然后通过position来找位置
  /// return: List<List<String>> 内层List表示一个段落中多个句子，外层List表示一个段落
  List<List<String>> splitTextEn(String text) {
    if (text.isEmpty) return [];
    try {
      List<String> paragraphs = text.split('\n\n');

      List<List<String>> result = [];

      // RegExp regExp = RegExp(r'(?<=[.,!?])\s+');
      // 只在标点后的空格/Tab处分句，保留手动的单行换行符\n
      RegExp regExp = RegExp(r'(?<=[.,!?])[ \t]+');

      for (String paragraph in paragraphs) {
        List<String> sentences = paragraph.split(regExp);

        List<String> sentenceList = [];
        for (int i = 0; i < sentences.length; i++) {
          if (sentences[i]
              .trim()
              .isEmpty) {
            continue;
          }
          sentenceList.add(sentences[i].trim() + " ");
        }

        if (sentenceList.isNotEmpty) {
          sentenceList[sentenceList.length - 1] = sentenceList.last.trimRight();
          result.add(sentenceList);
        }
      }

      return result;
    } catch (e) {
      print(e);
      LogE(tag: "LyricController", "------ splitText error = ${e.toString()}");
    }

    return [];
  }

  /// 通过下面算法来分割歌词（中文）
  /// 先通过\n\n来分割段落,然后通过中文标点符号来分割句子
  /// 中文断句标点：句号、问号、感叹号、分号、冒号、逗号、顿号、省略号、破折号
  /// 注意服务端返回的lrc必须跟这里算法保持一致，否则显示会有问题
  /// return: List<List<String>> 内层List表示一个段落中多个句子，外层List表示一个段落
  List<List<String>> splitTextZh(String text) {
    if (text.isEmpty) return [];
    try {
      List<String> paragraphs = text.split('\n\n');

      List<List<String>> result = [];

      // 中文断句标点：句号、问号、感叹号、分号、冒号、逗号、顿号、省略号、破折号
      // 在标点后断句（省略号和破折号可能连续出现，需要完整匹配）
      RegExp regExp = RegExp(r'(…+|—+|[。？！；：，、])');

      for (String paragraph in paragraphs) {
        // 在标点后插入换行符作为分隔
        String markedText = paragraph.replaceAllMapped(regExp, (match) => '${match.group(0)}\n');
        // 按换行符分割
        List<String> sentences = markedText.split('\n');

        List<String> sentenceList = [];
        for (String sentence in sentences) {
          if (sentence
              .trim()
              .isNotEmpty) {
            sentenceList.add(sentence.trim());
          }
        }

        if (sentenceList.isNotEmpty) {
          result.add(sentenceList);
        }
      }

      return result;
    } catch (e) {
      print(e);
      LogE(tag: "LyricController", "------ splitTextZh error = ${e.toString()}");
    }

    return [];
  }

  /// 检测文本是否为中文
  /// 通过检查是否包含中文标点符号来判断，速度快
  bool isChineseText(String text) {
    return RegExp(r'[。？！，、；：]').hasMatch(text);
  }
}
