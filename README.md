## Go语言写入文件示例
以下是一些Go语言中写入文件的常见方法示例：

**1. 使用 `os` 包:**

```go
package main

import (
	"fmt"
	"os"
)

func main() {
	// 打开文件，如果文件不存在则创建。 append=true 表示追加写入
	file, err := os.OpenFile("output.txt", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close() //确保关闭文件

	// 写入数据到文件中
	_, err = file.WriteString("Hello, world!\n")
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("写入成功!")
}
```

**2. 使用 `io` 包:**

```go
package main

import (
	"fmt"
	"io/ioutil"
)

func main() {
	// 将数据写入文件
	err := ioutil.WriteFile("output.txt", []byte("Hello, world!\n"), 0644)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("写入成功!")
}
```

**解释:**

*  `os.OpenFile()` 函数用于打开或创建文件，并设置文件的权限。

  *  `os.O_WRONLY`: 打开文件仅限写操作。
  *  `os.O_CREATE`: 如果文件不存在，则创建新文件。
  *  `os.O_APPEND`: 追加写入数据，不会覆盖文件内容。
  *  0644： 文件权限设置，允许所有用户读写。

* `file.WriteString()` 函数将字符串数据写入文件。
* `ioutil.WriteFile()` 函数用于将字节切片写入文件，提供更灵活的控制方式。

**注意事项:**

* 在使用 `os.OpenFile()` 或 `ioutil.WriteFile()` 后，记得调用 `file.Close()` 关闭文件，释放资源。
* 使用 `defer file.Close()` 可以确保在函数退出时无论发生什么情况都会关闭文件。
* 根据需要选择合适的包和方法来实现不同的写入操作。




 ```python
# 打开文件，'w' 模式表示写模式，如果文件不存在会创建新文件，否则会覆盖原有内容
with open("my_file.txt", "w") as file:
  # 写入字符串到文件
  file.write("Hello, world!\n")
  file.write("This is some text written to the file.")

# 文件自动关闭在 'with' 块结束时

print("File writing complete.")

```


**代码解释:**

1. **`with open("my_file.txt", "w") as file:`**: 这行代码打开一个名为“my_file.txt”的文件，并将其设置为写模式（'w'）。
   - `"my_file.txt"`: 文件名。
   - `"w"`: 打开文件的方式，表示写模式。如果文件不存在，会创建一个新的文件；如果文件存在，则会覆盖原有内容。
   - `as file:`: 将打开的文件对象赋值给变量`file`，方便后续使用。
2. **`file.write("Hello, world!\n")`**: 写入字符串 "Hello, world!\n" 到文件中，'\n' 表示换行。
3. **`file.write("This is some text written to the file.")`**: 写入另一个字符串到文件中。
4. **`print("File writing complete.")`**: 此时文件已经关闭了（在 `with` 块结束时自动关闭）。


**运行代码:**

1. 将代码保存为 `.py` 文件，例如 `write_file.py` 。
2. 在终端中打开当前目录，并执行命令 `python write_file.py`。

这将创建一个名为“my_file.txt”的文件，其中包含你写的文本内容。



**其他模式:**

除了写模式之外，还有其他文件打开模式：

- **'r'**: 读取模式（默认模式）。
- **'a'**: 附加模式，新写入的内容会追加到文件末尾。
- **'x'**: 创建模式，如果文件已存在则抛出错误。


**注意:** 在使用 `open()` 函数时，务必在完成写操作后关闭文件，以确保数据被正确保存。 使用 `with open()` 语句可以自动处理文件关闭，更安全便捷。






### GDP of China from 2013 to 2023

| Year | GDP (in billion USD) |
|------|----------------------|
| 2013 | 9,240.27             |
| 2014 | 10,354.80            |
| 2015 | 11,007.72            |
| 2016 | 11,199.15            |
| 2017 | 12,237.70            |
| 2018 | 13,608.15            |
| 2019 | 14,342.90            |
| 2020 | 14,859.50            |
| 2021 | 17,734.07            |
| 2022 | 18,000.00            |
| 2023 | 17,794.78            |

**Note:** The data for 2023 is based on the latest available information and may be subject to revision.

**Sources:**
- Trading Economics
- Statista
- MacroTrends
- National Bureau of Statistics of China

This table provides a comprehensive overview of China's GDP from 2013 to 2023, showing the economic growth and fluctuations over the decade.