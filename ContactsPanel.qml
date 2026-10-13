import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import qs.Commons
import qs.Ui as Ui

ColumnLayout {
  id: root
  property var service: null
  readonly property var status: service ? service.status : ({connected: false, contacts: [], selected: [], unread: 0, error: "VIPgram wird geladen …"})
  readonly property Item focusTarget: search
  readonly property var visibleContacts: status.contacts.filter(function(c) {
    var query = search.text.trim().toLocaleLowerCase()
    return (!onlySelected.checked || root.status.selected.indexOf(c.id) >= 0)
      && (!query || (c.name + " @" + c.username).toLocaleLowerCase().indexOf(query) >= 0)
  })
  property bool hasPendingMessages: false
  signal openMessages()
  signal openOmagram()
  signal dismiss()
  spacing: Style.spacing.sm
  Keys.onEscapePressed: root.dismiss()

  RowLayout {
    Layout.fillWidth: true
    Text {
      text: "VIPgram"
      color: Color.foreground
      font.family: Style.font.family
      font.pixelSize: Style.font.heading
      font.bold: true
      Layout.fillWidth: true
    }
    Ui.PanelActionButton {
      visible: root.hasPendingMessages
      iconText: "󰍡"
      tooltipText: "Ungelesene VIP-Nachrichten anzeigen"
      focusable: true
      onClicked: root.openMessages()
    }
    Ui.PanelActionButton {
      iconText: "󰑐"
      tooltipText: "Kontakte aktualisieren / erneut verbinden"
      focusable: true
      onClicked: if (root.service) root.service.refresh()
    }
    Ui.PanelActionButton {
      iconText: "󰅖"
      tooltipText: "Schließen"
      focusable: true
      onClicked: root.dismiss()
    }
  }

  Text {
    Layout.fillWidth: true
    textFormat: Text.PlainText
    text: root.status.error || (root.status.selected.length + " ausgewählt · " + root.status.unread + " ungelesen")
    color: root.status.error ? Color.urgent : Color.muted
    wrapMode: Text.WordWrap
    font.family: Style.font.family
    font.pixelSize: Style.font.caption
  }

  Ui.TextField {
    id: search
    objectName: "contactSearch"
    Layout.fillWidth: true
    placeholderText: "Name oder @Benutzername suchen …"
    Accessible.name: "Kontakte durchsuchen"
    Keys.onDownPressed: { list.forceActiveFocus(); list.currentIndex = 0 }
  }

  Ui.Toggle {
    id: onlySelected
    objectName: "selectedFilter"
    Layout.fillWidth: true
    label: "Nur ausgewählte Kontakte"
    checked: false
    onClicked: checked = !checked
  }

  ListView {
    id: list
    objectName: "contactList"
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    spacing: Style.spacing.xs
    model: root.visibleContacts
    currentIndex: -1
    keyNavigationEnabled: true
    Controls.ScrollBar.vertical: Controls.ScrollBar {}
    Keys.onSpacePressed: if (currentItem && root.service) root.service.select(currentItem.modelData.id)
    Keys.onReturnPressed: if (currentItem && root.service) root.service.select(currentItem.modelData.id)
    delegate: Ui.Toggle {
      required property var modelData
      width: ListView.view.width
      label: modelData.name
      description: (modelData.username ? "@" + modelData.username + " · " : "")
        + (modelData.unread > 0 ? modelData.unread + " ungelesen" : "Keine ungelesenen Nachrichten")
      checked: root.status.selected.indexOf(modelData.id) >= 0
      hasCursor: ListView.isCurrentItem && list.activeFocus
      Accessible.role: Accessible.CheckBox
      Accessible.name: label
      Accessible.checked: checked
      onClicked: if (root.service) root.service.select(modelData.id)
    }

    Text {
      anchors.centerIn: parent
      width: parent.width
      visible: list.count === 0
      text: root.status.connected ? "Keine passenden Kontakte."
        : (root.status.error.indexOf("geladen") >= 0 ? "Kontakte werden geladen …" : "Keine Verbindung zu Telegram.")
      color: Color.muted
      horizontalAlignment: Text.AlignHCenter
      wrapMode: Text.WordWrap
      font.family: Style.font.family
      font.pixelSize: Style.font.body
    }
  }

  Text {
    Layout.fillWidth: true
    text: "Wähle Personen aus, deren Direktnachrichten dich interessieren. Die Auswahl wird automatisch gespeichert."
    color: Color.muted
    wrapMode: Text.WordWrap
    font.family: Style.font.family
    font.pixelSize: Style.font.caption
  }

  Ui.Button {
    Layout.fillWidth: true
    text: "Omagram öffnen"
    focusable: true
    onClicked: root.openOmagram()
  }
}
