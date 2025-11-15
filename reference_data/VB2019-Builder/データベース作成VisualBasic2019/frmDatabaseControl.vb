Option Strict Off
Option Explicit On
Friend Class frmDatabaseControl
	Inherits System.Windows.Forms.Form
#Region "Windows フォーム デザイナによって生成されたコード"
	Public Sub New()
		MyBase.New()
		If m_vb6FormDefInstance Is Nothing Then
			If m_InitializingDefInstance Then
				m_vb6FormDefInstance = Me
			Else
				Try 
					'スタートアップ フォームについては、最初に作成されたインスタンスが既定インスタンスになります。
					If System.Reflection.Assembly.GetExecutingAssembly.EntryPoint.DeclaringType Is Me.GetType Then
						m_vb6FormDefInstance = Me
					End If
				Catch
				End Try
			End If
		End If
		'この呼び出しは、Windows フォーム デザイナで必要です。
		InitializeComponent()
	End Sub
	'Form は、コンポーネント一覧に後処理を実行するために dispose をオーバーライドします。
	Protected Overloads Overrides Sub Dispose(ByVal Disposing As Boolean)
		If Disposing Then
			If Not components Is Nothing Then
				components.Dispose()
			End If
		End If
		MyBase.Dispose(Disposing)
	End Sub
	'Windows フォーム デザイナで必要です。
	Private components As System.ComponentModel.IContainer
	Public ToolTip1 As System.Windows.Forms.ToolTip
	Public WithEvents txtPath As System.Windows.Forms.TextBox
	Public WithEvents cmdCompact As System.Windows.Forms.Button
	Public WithEvents cmdDelete As System.Windows.Forms.Button
	Public WithEvents cmdCreate As System.Windows.Forms.Button
	Public WithEvents Label1 As System.Windows.Forms.Label
	'メモ : 以下のプロシージャは Windows フォーム デザイナで必要です。
	'Windows フォーム デザイナを使って変更できます。
	'コードエディタを使って修正しないでください。


	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Me.ToolTip1 = New System.Windows.Forms.ToolTip(Me.components)
        Me.txtPath = New System.Windows.Forms.TextBox()
        Me.cmdCompact = New System.Windows.Forms.Button()
        Me.cmdDelete = New System.Windows.Forms.Button()
        Me.cmdCreate = New System.Windows.Forms.Button()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.SuspendLayout()
        '
        'txtPath
        '
        Me.txtPath.AcceptsReturn = True
        Me.txtPath.AutoSize = False
        Me.txtPath.BackColor = System.Drawing.SystemColors.Window
        Me.txtPath.Cursor = System.Windows.Forms.Cursors.IBeam
        Me.txtPath.ForeColor = System.Drawing.SystemColors.WindowText
        Me.txtPath.Location = New System.Drawing.Point(40, 32)
        Me.txtPath.MaxLength = 0
        Me.txtPath.Name = "txtPath"
        Me.txtPath.RightToLeft = System.Windows.Forms.RightToLeft.No
        Me.txtPath.Size = New System.Drawing.Size(185, 18)
        Me.txtPath.TabIndex = 3
        Me.txtPath.Text = "D:\Data.accdb"
        '
        'cmdCompact
        '
        Me.cmdCompact.BackColor = System.Drawing.SystemColors.Control
        Me.cmdCompact.Cursor = System.Windows.Forms.Cursors.Default
        Me.cmdCompact.ForeColor = System.Drawing.SystemColors.ControlText
        Me.cmdCompact.Location = New System.Drawing.Point(48, 144)
        Me.cmdCompact.Name = "cmdCompact"
        Me.cmdCompact.RightToLeft = System.Windows.Forms.RightToLeft.No
        Me.cmdCompact.Size = New System.Drawing.Size(177, 33)
        Me.cmdCompact.TabIndex = 2
        Me.cmdCompact.Text = "最適化"
        '
        'cmdDelete
        '
        Me.cmdDelete.BackColor = System.Drawing.SystemColors.Control
        Me.cmdDelete.Cursor = System.Windows.Forms.Cursors.Default
        Me.cmdDelete.ForeColor = System.Drawing.SystemColors.ControlText
        Me.cmdDelete.Location = New System.Drawing.Point(48, 104)
        Me.cmdDelete.Name = "cmdDelete"
        Me.cmdDelete.RightToLeft = System.Windows.Forms.RightToLeft.No
        Me.cmdDelete.Size = New System.Drawing.Size(177, 33)
        Me.cmdDelete.TabIndex = 1
        Me.cmdDelete.Text = "データベース削除"
        '
        'cmdCreate
        '
        Me.cmdCreate.BackColor = System.Drawing.SystemColors.Control
        Me.cmdCreate.Cursor = System.Windows.Forms.Cursors.Default
        Me.cmdCreate.ForeColor = System.Drawing.SystemColors.ControlText
        Me.cmdCreate.Location = New System.Drawing.Point(48, 64)
        Me.cmdCreate.Name = "cmdCreate"
        Me.cmdCreate.RightToLeft = System.Windows.Forms.RightToLeft.No
        Me.cmdCreate.Size = New System.Drawing.Size(177, 33)
        Me.cmdCreate.TabIndex = 0
        Me.cmdCreate.Text = "データベース作成"
        '
        'Label1
        '
        Me.Label1.BackColor = System.Drawing.SystemColors.Control
        Me.Label1.Cursor = System.Windows.Forms.Cursors.Default
        Me.Label1.ForeColor = System.Drawing.SystemColors.ControlText
        Me.Label1.Location = New System.Drawing.Point(40, 16)
        Me.Label1.Name = "Label1"
        Me.Label1.RightToLeft = System.Windows.Forms.RightToLeft.No
        Me.Label1.Size = New System.Drawing.Size(57, 17)
        Me.Label1.TabIndex = 4
        Me.Label1.Text = "パス"
        '
        'frmDatabaseControl
        '
        Me.AutoScaleBaseSize = New System.Drawing.Size(5, 12)
        Me.ClientSize = New System.Drawing.Size(260, 201)
        Me.Controls.AddRange(New System.Windows.Forms.Control() {Me.txtPath, Me.cmdCompact, Me.cmdDelete, Me.cmdCreate, Me.Label1})
        Me.Location = New System.Drawing.Point(4, 23)
        Me.Name = "frmDatabaseControl"
        Me.Text = "競走馬データ読み込み"
        Me.ResumeLayout(False)

    End Sub
#End Region 
#Region "アップグレード ウィザードのサポート コード"
	Private Shared m_vb6FormDefInstance As frmDatabaseControl
	Private Shared m_InitializingDefInstance As Boolean
	Public Shared Property DefInstance() As frmDatabaseControl
		Get
			If m_vb6FormDefInstance Is Nothing OrElse m_vb6FormDefInstance.IsDisposed Then
				m_InitializingDefInstance = True
				m_vb6FormDefInstance = New frmDatabaseControl()
				m_InitializingDefInstance = False
			End If
			DefInstance = m_vb6FormDefInstance
		End Get
		Set
			m_vb6FormDefInstance = Value
		End Set
	End Property
#End Region 
	'========================================================================
	'  JRA-VAN Data Lab. プログラミングパーツ「サンプルプログラム」
	'
	'
    '   作成: JRA-VAN ソフトウェア工房
	'
	'========================================================================
	'   (C) Copyright Turf Media System Co.,Ltd. 2003 All rights reserved
	'========================================================================
	
	
	Private objDBControl As clsDBBuilder
	
	'DB作成
	Private Sub cmdCreate_Click(ByVal eventSender As System.Object, ByVal eventArgs As System.EventArgs) Handles cmdCreate.Click
		objDBControl = New clsDBBuilder
		If objDBControl.CreateDB(txtPath.Text) = True Then
			MsgBox(txtPath.Text & "にDBを作成しました。")
		Else
			MsgBox("エラー：DB作成に失敗しました。")
		End If
		

        objDBControl = Nothing
    End Sub

    'DB消去
    Private Sub cmdDelete_Click(ByVal eventSender As System.Object, ByVal eventArgs As System.EventArgs) Handles cmdDelete.Click
        objDBControl = New clsDBBuilder()
        If objDBControl.KillDB(txtPath.Text) = True Then
            MsgBox(txtPath.Text & "を削除しました。")
        Else
            MsgBox("エラー：削除に失敗しました。")
        End If

        objDBControl = Nothing
    End Sub

    'DB最適化
    Private Sub cmdCompact_Click(ByVal eventSender As System.Object, ByVal eventArgs As System.EventArgs) Handles cmdCompact.Click
        objDBControl = New clsDBBuilder()
        If objDBControl.CompactDB(txtPath.Text) = True Then
            MsgBox(txtPath.Text & "の最適化に成功しました。")
        Else
            MsgBox("エラー：最適化に失敗しました。")
        End If

        objDBControl = Nothing
    End Sub

End Class