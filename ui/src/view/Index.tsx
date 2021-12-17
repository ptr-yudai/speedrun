import kureanifURL from "../assets/kurenaif.png";
import rekkusuURL from "../assets/rekkusu.png";
import ptrYudaiURL from "../assets/ptr-yudai.jpeg";
import keymoonURL from "../assets/keymoon.jpg";
import moratorium08URL from "../assets/moratorium08.png";
import theoremoonURL from "../assets/theoldmoon0602.png";

const Index = () => {
  return (
    <>
      <section>
        <h1>Speedrun Challenge</h1>

        <h2>出演</h2>
        <div className="admin-flex">
          <a href="https://twitter.com/xrekkusu" className="admin">
              <img src={rekkusuURL} className="admin-icon" />
              <p className="admin-description">司会・実況</p>
          </a>

          <a href="https://twitter.com/ptrYudai" className="admin">
            <img src={ptrYudaiURL} className="admin-icon" />
            <p className="admin-description">作問・実況</p>
          </a>

          <a href="https://twitter.com/fwarashi" className="admin">
            <img src={kureanifURL} className="admin-icon" />
            <p className="admin-description">crypto走者</p>
          </a>

          <a href="https://twitter.com/theoremoon" className="admin">
            <img src={theoremoonURL} className="admin-icon" />
            <p className="admin-description">crypto走者</p>
          </a>

          <a href="https://twitter.com/moratorium08" className="admin">
            <img src={moratorium08URL} className="admin-icon" />
            <p className="admin-description">pwn走者</p>
          </a>

          <a href="https://twitter.com/kymn_" className="admin">
            <img src={keymoonURL} className="admin-icon" />
            <p className="admin-description">pwn走者</p>
          </a>
        </div>
      </section>

      <section>
        <h2>配信</h2>
        <p>12月19日（日） 15:40(JST) 〜</p>
        <div style={{display: "flex", justifyContent: "space-around", flexWrap: "wrap"}}>
          <div style={{margin: "0 20px"}}>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/VXaROnAmAiY" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
          </div>
          <div style={{margin: "0 20px"}}>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/tDkNKz0qMW4" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
          </div>
        </div>
      </section>


      <section>
        <h2>Rule</h2>
        <ul>
          <li><p>このCTFは個人戦です（1人1アカウント）</p></li>
          <li><p>問題を速く解いた人ほど順位が高くなります（各問題にランキングがあります）</p></li>
          <li><p>スコアサーバーを攻撃・破壊する行為は禁止します。</p></li>
          <li><p>開始時刻：上記配信内で開始されます</p></li>
          <li><p>終了時刻：そのうち終了します</p></li>
        </ul>
      </section>

      <section>
        <h2>遊び方</h2>
        <p>問題をクリックして「START」を押すと問題が表示され、時間の測定が開始します。正しいフラグを提出した時点でタイマーが止まります。（welcome問で動作を確認してください。）</p>
        <p>問題を解いている間に別の問題を解き始めることも可能ですが、開いている問題のタイマーはフラグを提出するまで停止しません。</p>
      </section>

      <section>
        <h2>FAQ</h2>
        <h4>Q. ログイン情報を忘れました</h4>
        <p>諦めてください</p>
      </section>
    </>
  );
};
export default Index;
